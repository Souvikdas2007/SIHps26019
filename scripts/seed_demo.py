"""Seed a clearly labeled synthetic offline demo bundle."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Settings
from core.data.catalog import ingest_geojson
from core.database.connection import connect
from core.database.migrator import apply_migrations
from core.evidence import index_document
from core.profiles import DatasetProfile, VersionedProfile


DEMO_GEOJSON = {
    "type": "FeatureCollection",
    "name": "synthetic-kolkata-peri-urban-lulc-demo",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "spatial_unit_id": "unit-001",
                "observed_year": 2020,
                "land_use_class": "agriculture",
                "area_sq_m": 10000,
            },
            "geometry": {"type": "Polygon", "coordinates": [[[88.40, 22.50], [88.41, 22.50], [88.41, 22.51], [88.40, 22.50]]]},
        },
        {
            "type": "Feature",
            "properties": {
                "spatial_unit_id": "unit-001",
                "observed_year": 2024,
                "land_use_class": "built_up",
                "area_sq_m": 10000,
            },
            "geometry": {"type": "Polygon", "coordinates": [[[88.40, 22.50], [88.41, 22.50], [88.41, 22.51], [88.40, 22.50]]]},
        },
        {
            "type": "Feature",
            "properties": {
                "spatial_unit_id": "unit-002",
                "observed_year": 2020,
                "land_use_class": "built_up",
                "area_sq_m": 8000,
            },
            "geometry": {"type": "Polygon", "coordinates": [[[88.41, 22.50], [88.42, 22.50], [88.42, 22.51], [88.41, 22.50]]]},
        },
    ],
}


def main() -> None:
    settings = Settings.from_environment()
    apply_migrations(settings.database_path)
    asset_path = PROJECT_ROOT / "data" / "processed" / "synthetic-kolkata-lulc.geojson"
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    if not asset_path.exists():
        asset_path.write_text(json.dumps(DEMO_GEOJSON, indent=2), encoding="utf-8")

    dataset = DatasetProfile(
        identifier="synthetic-kolkata-lulc",
        version="demo-v1",
        display_name="Synthetic Kolkata LULC Demo",
        source="PS26019 synthetic test/demo fixture",
        source_url=None,
        data_year=2024,
        crs="EPSG:4326",
        asset_path=str(asset_path),
    )
    region = VersionedProfile(
        identifier="synthetic-kolkata-peri-urban",
        version="demo-v1",
        display_name="Synthetic Kolkata peri-urban study area",
    )

    with connect(settings.database_path) as connection:
        existing = connection.execute(
            "SELECT id FROM datasets WHERE profile_identifier = ? AND name = ?",
            (dataset.identifier, dataset.display_name),
        ).fetchone()
        if existing:
            print("Synthetic demo bundle already seeded")
            return
        summary = ingest_geojson(connection, dataset, region, asset_path)
        index_document(
            connection,
            source_id="synthetic-policy-001",
            title="Synthetic Urban Land Policy Note",
            source="PS26019 synthetic test/demo corpus",
            file_path="data/documents/synthetic-policy-001.txt",
            chunks=[
                "Controlled agricultural conversion should preserve environmental constraints.",
                "Urban proximity and infrastructure access can be used as explanatory suitability factors.",
                "This synthetic note is demonstration evidence, not an official government source.",
            ],
            document_type="synthetic-demo",
        )
    print(f"Seeded synthetic demo: {summary.observation_count} observations")


if __name__ == "__main__":
    main()
