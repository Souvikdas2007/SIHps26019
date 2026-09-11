import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from backend.config import Settings
from backend.security import (
    create_session,
    get_user_for_token,
    hash_password,
    verify_password,
    write_audit,
)
from ai.synthesis import build_grounded_insight
from core.analytics import LandUseObservation, summarize_land_use
from core.database.connection import connect
from core.database.migrator import apply_migrations
from core.data.catalog import ingest_geojson
from core.evidence import index_document, search_evidence
from core.profiles import DatasetProfile, ScenarioConfig, VersionedProfile
from core.simulation import CandidateArea, ScenarioParameters, run_conversion_scenario


FAKE_LULC_DATASET = {
    "type": "FeatureCollection",
    "name": "synthetic-kolkata-peri-urban-lulc",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "spatial_unit_id": "unit-001",
                "observed_year": 2020,
                "land_use_class": "agriculture",
                "area_sq_m": 10000,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[88.40, 22.50], [88.41, 22.50], [88.41, 22.51], [88.40, 22.50]]],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "spatial_unit_id": "unit-001",
                "observed_year": 2024,
                "land_use_class": "built_up",
                "area_sq_m": 10000,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[88.40, 22.50], [88.41, 22.50], [88.41, 22.51], [88.40, 22.50]]],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "spatial_unit_id": "unit-002",
                "observed_year": 2020,
                "land_use_class": "built_up",
                "area_sq_m": 8000,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[88.41, 22.50], [88.42, 22.50], [88.42, 22.51], [88.41, 22.50]]],
            },
        },
    ],
}


class FoundationTests(unittest.TestCase):
    def test_migrations_create_schema_and_are_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "ps26019.db"
            self.assertEqual(apply_migrations(database_path), 3)
            self.assertEqual(apply_migrations(database_path), 0)

            with connect(database_path) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual table')"
                    )
                }
                self.assertIn("scenario_results", tables)
                self.assertIn("document_chunks_fts", tables)
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0], 4
                )
                self.assertEqual(
                    connection.execute("PRAGMA foreign_keys").fetchone()[0], 1
                )

    def test_foreign_keys_reject_orphan_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "ps26019.db"
            apply_migrations(database_path)
            with connect(database_path) as connection:
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO dataset_versions "
                        "(dataset_id, version, asset_path) VALUES (?, ?, ?)",
                        (999, "v1", "data/processed/missing.gpkg"),
                    )

    def test_profiles_keep_unresolved_choices_replaceable(self) -> None:
        dataset = DatasetProfile(
            identifier="lulc-kolkata-demo",
            version="v1",
            display_name="Kolkata demonstration LULC",
            source="prepared local bundle",
            source_url=None,
            data_year=None,
            crs=None,
            asset_path="data/processed/lulc/demo.gpkg",
        )
        scenario = ScenarioConfig(
            identifier="agri-to-built-up",
            version="v1",
            display_name="Controlled agricultural conversion",
            factors=("urban_proximity", "infrastructure_access"),
            weights={"urban_proximity": 0.6, "infrastructure_access": 0.4},
            assumptions=("scenario analysis only",),
        )
        self.assertEqual(dataset.identifier, "lulc-kolkata-demo")
        self.assertAlmostEqual(sum(scenario.weights.values()), 1.0)

    def test_fake_lulc_dataset_registers_provenance_and_observations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "ps26019.db"
            geojson_path = Path(temporary_directory) / "fake-lulc.geojson"
            geojson_path.write_text(json.dumps(FAKE_LULC_DATASET), encoding="utf-8")
            apply_migrations(database_path)

            dataset = DatasetProfile(
                identifier="synthetic-kolkata-lulc",
                version="test-v1",
                display_name="Synthetic Kolkata LULC",
                source="test fixture",
                source_url=None,
                data_year=2024,
                crs="EPSG:4326",
                asset_path=str(geojson_path),
            )
            region = VersionedProfile(
                identifier="synthetic-kolkata-peri-urban",
                version="test-v1",
                display_name="Synthetic Kolkata peri-urban area",
            )

            with connect(database_path) as connection:
                summary = ingest_geojson(connection, dataset, region, geojson_path)
                self.assertEqual(summary.observation_count, 3)
                self.assertEqual(len(summary.asset_checksum), 64)
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM datasets").fetchone()[0], 1
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM landuse_observations").fetchone()[0],
                    3,
                )
                self.assertEqual(
                    connection.execute("SELECT crs FROM dataset_versions").fetchone()[0],
                    "EPSG:4326",
                )
                self.assertEqual(
                    connection.execute("SELECT profile_identifier FROM datasets").fetchone()[0],
                    "synthetic-kolkata-lulc",
                )

    def test_fake_lulc_dataset_rejects_missing_observation_property(self) -> None:
        invalid_dataset = json.loads(json.dumps(FAKE_LULC_DATASET))
        del invalid_dataset["features"][0]["properties"]["area_sq_m"]
        with tempfile.TemporaryDirectory() as temporary_directory:
            geojson_path = Path(temporary_directory) / "invalid.geojson"
            geojson_path.write_text(json.dumps(invalid_dataset), encoding="utf-8")
            with self.assertRaises(ValueError):
                with connect(Path(temporary_directory) / "ps26019.db") as connection:
                    apply_migrations(Path(temporary_directory) / "ps26019.db")
                    ingest_geojson(
                        connection,
                        DatasetProfile(
                            identifier="invalid",
                            version="test-v1",
                            display_name="Invalid fixture",
                            source="test fixture",
                            source_url=None,
                            data_year=2024,
                            crs="EPSG:4326",
                            asset_path=str(geojson_path),
                        ),
                        VersionedProfile("invalid-region", "test-v1", "Invalid region"),
                        geojson_path,
                    )

    def test_database_url_must_be_sqlite(self) -> None:
        with patch.dict("os.environ", {"DATABASE_URL": "postgresql://localhost/db"}):
            with self.assertRaises(ValueError):
                Settings.from_environment()

    def test_production_rejects_non_https_cors_origins(self) -> None:
        with patch.dict(
            "os.environ",
            {"APP_ENV": "production", "CORS_ORIGINS": "http://localhost:5173"},
        ):
            with self.assertRaises(ValueError):
                Settings.from_environment()

    def test_land_use_analytics_are_deterministic(self) -> None:
        observations = [
            LandUseObservation("unit-001", 2020, "agriculture", 10000),
            LandUseObservation("unit-001", 2024, "built_up", 10000),
            LandUseObservation("unit-002", 2020, "built_up", 8000),
        ]
        summary = summarize_land_use(observations)
        self.assertEqual(summary.totals_by_year[2020]["agriculture"], 10000)
        self.assertEqual(summary.totals_by_year[2024]["built_up"], 10000)
        self.assertEqual(summary.change_between_periods["agriculture"], -10000)
        self.assertEqual(summary.change_between_periods["built_up"], 2000)

    def test_local_evidence_search_returns_source_attribution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "ps26019.db"
            apply_migrations(database_path)
            with connect(database_path) as connection:
                index_document(
                    connection,
                    source_id="synthetic-policy-001",
                    title="Synthetic Urban Land Policy Note",
                    source="test corpus",
                    file_path="data/documents/synthetic-policy.txt",
                    chunks=[
                        "Controlled agricultural conversion should preserve environmental constraints.",
                        "Urban proximity can be used as an explanatory suitability factor.",
                    ],
                )
                results = search_evidence(connection, "agricultural conversion")
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0].source_id, "synthetic-policy-001")
                self.assertIn("agricultural", results[0].snippet)

    def test_scenario_simulation_is_deterministic_and_explainable(self) -> None:
        candidates = [
            CandidateArea("unit-001", "agriculture", 10000, 0.9, 0.7, 0.8, 0.1),
            CandidateArea("unit-002", "agriculture", 8000, 0.6, 0.8, 0.7, 0.4),
            CandidateArea("unit-003", "agriculture", 6000, 0.8, 0.4, 0.5, 0.9),
            CandidateArea("unit-004", "built_up", 5000, 1.0, 1.0, 1.0, 0.0),
        ]
        parameters = ScenarioParameters(
            requested_area_sq_m=9000,
            target_land_use_class="built_up",
            weights={
                "urban_proximity": 0.4,
                "population_pressure": 0.2,
                "infrastructure_access": 0.3,
                "environmental_constraint": 0.1,
            },
            scenario_version="test-v1",
            assumptions=("synthetic factors",),
        )
        first = run_conversion_scenario(candidates, parameters)
        second = run_conversion_scenario(candidates, parameters)
        self.assertEqual(first.as_dict(), second.as_dict())
        self.assertEqual(first.selected_units, ("unit-001",))
        self.assertEqual(first.allocated_area_sq_m, 9000)
        self.assertEqual(first.scenario_area_by_class["built_up"], 14000)
        self.assertIn("not an authoritative prediction", first.limitation)

    def test_ai_fallback_keeps_deterministic_result_when_runtime_is_offline(self) -> None:
        class OfflineProvider:
            def health(self) -> bool:
                return False

            def generate(self, prompt: str, context: dict) -> str:
                raise AssertionError("offline provider must not generate")

        insight = build_grounded_insight(
            OfflineProvider(),
            question="Where is conversion most suitable?",
            evidence=[],
            scenario_result={"allocated_area_sq_m": 9000},
            assumptions=["synthetic test scenario"],
        )
        self.assertEqual(insight.status, "unavailable")
        self.assertEqual(insight.scenario_result["allocated_area_sq_m"], 9000)
        self.assertIn("unavailable", insight.summary)

    def test_local_auth_hashes_passwords_and_records_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "ps26019.db"
            apply_migrations(database_path)
            encoded = hash_password("correct horse battery staple")
            self.assertTrue(verify_password("correct horse battery staple", encoded))
            self.assertFalse(verify_password("wrong password", encoded))
            with connect(database_path) as connection:
                role_id = connection.execute(
                    "SELECT id FROM roles WHERE name = 'ADMIN'"
                ).fetchone()[0]
                user_id = connection.execute(
                    "INSERT INTO users (username, password_hash, role_id) VALUES (?, ?, ?)",
                    ("test-admin", encoded, role_id),
                ).lastrowid
                token = create_session(connection, user_id, hours=1)
                user = get_user_for_token(connection, token)
                write_audit(connection, event_type="TEST_EVENT", user_id=user_id)
                self.assertEqual(user.username, "test-admin")
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0], 1
                )


if __name__ == "__main__":
    unittest.main()
