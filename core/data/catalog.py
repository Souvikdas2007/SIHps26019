"""Dependency-free registration of prepared GeoJSON datasets."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any

from core.profiles import DatasetProfile, VersionedProfile


@dataclass(frozen=True)
class IngestionSummary:
    dataset_id: int
    dataset_version_id: int
    region_id: int
    observation_count: int
    asset_checksum: str


def ingest_geojson(
    connection: sqlite3.Connection,
    dataset: DatasetProfile,
    region: VersionedProfile,
    geojson_path: Path,
    *,
    publisher: str = "synthetic test fixture",
    license_terms: str = "internal test data only",
    processing_steps: str = "validated GeoJSON fixture",
) -> IngestionSummary:
    """Register a GeoJSON LULC asset and its observation properties.

    This importer intentionally handles the small prepared MVP contract only.
    GeoPandas/Shapely remain responsible for production geometry operations.
    """
    payload = json.loads(geojson_path.read_text(encoding="utf-8"))
    _validate_feature_collection(payload)
    checksum = hashlib.sha256(geojson_path.read_bytes()).hexdigest()

    dataset_id = _insert_dataset(connection, dataset, publisher, license_terms)
    dataset_version_id = _insert_dataset_version(
        connection,
        dataset_id,
        dataset,
        geojson_path,
        checksum,
        processing_steps,
    )
    region_id = _insert_region(connection, region, dataset_version_id, dataset.crs)

    observation_count = 0
    for feature in payload["features"]:
        properties = feature["properties"]
        connection.execute(
            """
            INSERT INTO landuse_observations (
                dataset_version_id, region_id, spatial_unit_id,
                observed_year, land_use_class, area_sq_m, geometry_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_version_id,
                region_id,
                _required_property(properties, "spatial_unit_id"),
                _required_property(properties, "observed_year"),
                _required_property(properties, "land_use_class"),
                _required_property(properties, "area_sq_m"),
                str(geojson_path),
            ),
        )
        observation_count += 1

    return IngestionSummary(
        dataset_id=dataset_id,
        dataset_version_id=dataset_version_id,
        region_id=region_id,
        observation_count=observation_count,
        asset_checksum=checksum,
    )


def _insert_dataset(
    connection: sqlite3.Connection,
    dataset: DatasetProfile,
    publisher: str,
    license_terms: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO datasets (
            name, profile_identifier, source, source_url,
            publisher, license_terms, description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dataset.display_name,
            dataset.identifier,
            dataset.source,
            dataset.source_url,
            publisher,
            license_terms,
            "Versioned prepared land-use observations",
        ),
    )
    return int(cursor.lastrowid)


def _insert_dataset_version(
    connection: sqlite3.Connection,
    dataset_id: int,
    dataset: DatasetProfile,
    geojson_path: Path,
    checksum: str,
    processing_steps: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO dataset_versions (
            dataset_id, version, data_year, spatial_resolution,
            crs, processing_steps, asset_path, checksum
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            dataset_id,
            dataset.version,
            dataset.data_year,
            "synthetic unit",
            dataset.crs,
            processing_steps,
            str(geojson_path),
            checksum,
        ),
    )
    return int(cursor.lastrowid)


def _insert_region(
    connection: sqlite3.Connection,
    region: VersionedProfile,
    dataset_version_id: int,
    crs: str | None,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO regions (
            identifier, name, profile_version,
            source_dataset_version_id, geometry_path, crs, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            region.identifier,
            region.display_name,
            region.version,
            dataset_version_id,
            None,
            crs,
            "Synthetic bounded study area profile",
        ),
    )
    return int(cursor.lastrowid)


def _validate_feature_collection(payload: Any) -> None:
    if payload.get("type") != "FeatureCollection" or not payload.get("features"):
        raise ValueError("GeoJSON must be a non-empty FeatureCollection")
    for feature in payload["features"]:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") != "Polygon" or not geometry.get("coordinates"):
            raise ValueError("Each fixture feature must contain a Polygon geometry")
        if not isinstance(feature.get("properties"), dict):
            raise ValueError("Each fixture feature must contain properties")


def _required_property(properties: dict[str, Any], name: str) -> Any:
    value = properties.get(name)
    if value is None:
        raise ValueError(f"Missing required observation property: {name}")
    return value
