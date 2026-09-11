"""FastAPI application for the PS26019 local MVP."""

from dataclasses import asdict
import hashlib
import json
import uuid
from pathlib import Path
import sqlite3
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai.providers.llama_cpp import LlamaCppProvider
from ai.synthesis import build_grounded_insight
from backend.config import Settings
from backend.security import (
    AuthenticatedUser,
    create_session,
    get_user_for_token,
    verify_password,
    write_audit,
)
from core.analytics import LandUseObservation, summarize_land_use
from core.database.connection import connect
from core.database.migrator import apply_migrations
from core.evidence import search_evidence
from core.profiles import DatasetProfile, VersionedProfile
from core.simulation import CandidateArea, ScenarioParameters, run_conversion_scenario


settings = Settings.from_environment()
app = FastAPI(title="PS26019 Local MVP", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if settings.app_env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


class ScenarioCandidateRequest(BaseModel):
    spatial_unit_id: str
    land_use_class: str
    area_sq_m: float = Field(ge=0)
    urban_proximity: float = Field(ge=0, le=1)
    population_pressure: float = Field(ge=0, le=1)
    infrastructure_access: float = Field(ge=0, le=1)
    environmental_constraint: float = Field(ge=0, le=1)
    eligible: bool = True


class ScenarioRequest(BaseModel):
    candidates: list[ScenarioCandidateRequest]
    requested_area_sq_m: float = Field(ge=0)
    target_land_use_class: str = "built_up"
    weights: dict[str, float]
    scenario_version: str = "demo-v1"
    assumptions: list[str] = Field(default_factory=list)


class InsightRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    evidence_query: str = ""
    scenario_result: dict[str, Any] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class DatasetRegistrationRequest(BaseModel):
    profile_identifier: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    version: str = Field(min_length=1, max_length=50)
    display_name: str = Field(min_length=1, max_length=200)
    source: str = Field(min_length=1, max_length=500)
    source_url: str | None = Field(default=None, max_length=1000)
    data_year: int | None = Field(default=None, ge=1900, le=2100)
    crs: str | None = Field(default=None, max_length=50)
    asset_path: str = Field(min_length=1, max_length=500)
    region_identifier: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    region_version: str = Field(min_length=1, max_length=50)
    region_display_name: str = Field(min_length=1, max_length=200)


class ModelRegistrationRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=100)
    runtime: str = Field(min_length=1, max_length=100)
    model_name: str = Field(min_length=1, max_length=200)
    model_version: str = Field(min_length=1, max_length=100)
    model_format: str = Field(min_length=1, max_length=50)
    asset_path: str | None = Field(default=None, max_length=500)
    checksum: str | None = Field(default=None, min_length=64, max_length=64, pattern=r"^[a-fA-F0-9]{64}$")


@app.on_event("startup")
def initialize_database() -> None:
    apply_migrations(settings.database_path)


@app.get("/api/health")
def health() -> dict[str, Any]:
    provider = LlamaCppProvider(settings.llama_cpp_base_url, settings.llama_cpp_model)
    with connect(settings.database_path) as connection:
        connection.execute("SELECT 1")
    return {
        "status": "ok",
        "database": "connected",
        "llm_provider": settings.llm_provider,
        "llm_runtime": settings.llm_runtime,
        "llm_available": provider.health(),
    }


@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict[str, str]:
    with connect(settings.database_path) as connection:
        row = connection.execute(
            """
            SELECT u.id, u.password_hash
            FROM users AS u
            WHERE u.username = ? AND u.is_active = 1
            """,
            (request.username,),
        ).fetchone()
        if row is None or not verify_password(request.password, row[1]):
            write_audit(connection, event_type="AUTH_LOGIN_FAILED", details_json=json.dumps({"username": request.username}))
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_session(connection, row[0])
        write_audit(connection, event_type="AUTH_LOGIN_SUCCESS", user_id=row[0])
    return {"access_token": token, "token_type": "bearer"}


def require_user(authorization: str | None = Header(default=None)) -> AuthenticatedUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization[7:].strip()
    with connect(settings.database_path) as connection:
        user = get_user_for_token(connection, token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user


def require_roles(*allowed_roles: str):
    def dependency(user: AuthenticatedUser = Depends(require_user)) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            with connect(settings.database_path) as connection:
                write_audit(
                    connection,
                    event_type="AUTHORIZATION_DENIED",
                    user_id=user.id,
                    details_json=json.dumps({"required_roles": allowed_roles}),
                )
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return dependency


def _local_asset_path(asset_path: str, directory_name: str) -> Path:
    candidate = (Path(__file__).resolve().parents[1] / asset_path).resolve()
    allowed_root = (Path(__file__).resolve().parents[1] / directory_name).resolve()
    if not candidate.is_relative_to(allowed_root):
        raise HTTPException(status_code=400, detail=f"Asset must be inside {directory_name}/")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Asset file was not found")
    return candidate


@app.get("/api/catalog")
def catalog(
    user: AuthenticatedUser = Depends(require_user),
) -> dict[str, list[dict[str, Any]]]:
    del user
    with connect(settings.database_path) as connection:
        dataset_rows = connection.execute(
            """
            SELECT d.id, d.profile_identifier, d.name, d.source, d.source_url,
                   d.publisher, d.license_terms, d.description,
                   dv.id, dv.version, dv.data_year, dv.crs, dv.asset_path,
                   dv.checksum, dv.created_at
            FROM datasets AS d
            LEFT JOIN dataset_versions AS dv ON dv.dataset_id = d.id
            ORDER BY d.name, dv.version
            """
        ).fetchall()
        model_rows = connection.execute(
            """
            SELECT id, provider, runtime, model_name, model_version,
                   model_format, asset_path, checksum, created_at
            FROM model_versions
            ORDER BY model_name, model_version
            """
        ).fetchall()

    datasets: dict[int, dict[str, Any]] = {}
    for row in dataset_rows:
        dataset = datasets.setdefault(
            row[0],
            {
                "id": row[0],
                "profile_identifier": row[1],
                "name": row[2],
                "source": row[3],
                "source_url": row[4],
                "publisher": row[5],
                "license_terms": row[6],
                "description": row[7],
                "versions": [],
            },
        )
        if row[8] is not None:
            dataset["versions"].append(
                {
                    "id": row[8],
                    "version": row[9],
                    "data_year": row[10],
                    "crs": row[11],
                    "asset_path": row[12],
                    "checksum": row[13],
                    "created_at": row[14],
                }
            )
    return {
        "datasets": list(datasets.values()),
        "models": [
            {
                "id": row[0],
                "provider": row[1],
                "runtime": row[2],
                "model_name": row[3],
                "model_version": row[4],
                "model_format": row[5],
                "asset_path": row[6],
                "checksum": row[7],
                "created_at": row[8],
            }
            for row in model_rows
        ],
    }


@app.post("/api/catalog/datasets", status_code=201)
def register_dataset(
    request: DatasetRegistrationRequest,
    user: AuthenticatedUser = Depends(require_roles("ADMIN", "RESEARCHER")),
) -> dict[str, Any]:
    asset_path = _local_asset_path(request.asset_path, "data")
    if asset_path.suffix.lower() != ".geojson":
        raise HTTPException(status_code=400, detail="Only prepared GeoJSON assets are supported")
    dataset = DatasetProfile(
        identifier=request.profile_identifier,
        version=request.version,
        display_name=request.display_name,
        source=request.source,
        source_url=request.source_url,
        data_year=request.data_year,
        crs=request.crs,
        asset_path=request.asset_path,
    )
    region = VersionedProfile(
        identifier=request.region_identifier,
        version=request.region_version,
        display_name=request.region_display_name,
    )
    try:
        from core.data.catalog import ingest_geojson

        with connect(settings.database_path) as connection:
            summary = ingest_geojson(connection, dataset, region, asset_path, publisher=user.username)
            write_audit(
                connection,
                event_type="DATASET_REGISTERED",
                user_id=user.id,
                entity_type="dataset_version",
                entity_id=str(summary.dataset_version_id),
                details_json=json.dumps({"profile_identifier": request.profile_identifier}),
            )
    except (ValueError, sqlite3.IntegrityError) as error:
        raise HTTPException(status_code=409, detail=f"Dataset registration failed: {error}") from error
    return {
        "dataset_id": summary.dataset_id,
        "dataset_version_id": summary.dataset_version_id,
        "region_id": summary.region_id,
        "observation_count": summary.observation_count,
        "asset_checksum": summary.asset_checksum,
    }


@app.post("/api/catalog/models", status_code=201)
def register_model(
    request: ModelRegistrationRequest,
    user: AuthenticatedUser = Depends(require_roles("ADMIN")),
) -> dict[str, Any]:
    if request.asset_path:
        _local_asset_path(request.asset_path, "models")
    try:
        with connect(settings.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO model_versions (
                    provider, runtime, model_name, model_version,
                    model_format, asset_path, checksum
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.provider,
                    request.runtime,
                    request.model_name,
                    request.model_version,
                    request.model_format,
                    request.asset_path,
                    request.checksum,
                ),
            )
            write_audit(
                connection,
                event_type="MODEL_REGISTERED",
                user_id=user.id,
                entity_type="model_version",
                entity_id=str(cursor.lastrowid),
                details_json=json.dumps({"model_name": request.model_name}),
            )
            model_id = cursor.lastrowid
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail=f"Model registration failed: {error}") from error
    return {"model_id": model_id}


@app.get("/api/evidence")
def evidence_search(
    query: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[dict[str, Any]]:
    with connect(settings.database_path) as connection:
        return [asdict(result) for result in search_evidence(connection, query, limit=limit)]


@app.get("/api/analytics")
def analytics(region_id: int | None = None) -> dict[str, Any]:
    query = """
        SELECT spatial_unit_id, observed_year, land_use_class, area_sq_m
        FROM landuse_observations
    """
    parameters: tuple[Any, ...] = ()
    if region_id is not None:
        query += " WHERE region_id = ?"
        parameters = (region_id,)
    with connect(settings.database_path) as connection:
        rows = connection.execute(query, parameters).fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No land-use observations found")
    observations = [LandUseObservation(*tuple(row)) for row in rows]
    return summarize_land_use(observations).as_dict()


@app.post("/api/scenarios/run")
def run_scenario(
    request: ScenarioRequest,
    user: AuthenticatedUser = Depends(require_roles("ADMIN", "POLICY_ANALYST")),
) -> dict[str, Any]:
    candidates = [CandidateArea(**candidate.model_dump()) for candidate in request.candidates]
    parameters = ScenarioParameters(
        requested_area_sq_m=request.requested_area_sq_m,
        target_land_use_class=request.target_land_use_class,
        weights=request.weights,
        scenario_version=request.scenario_version,
        assumptions=tuple(request.assumptions),
    )
    try:
        result = run_conversion_scenario(candidates, parameters)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    result_payload = result.as_dict()
    scenario_identifier = f"scenario-{uuid.uuid4().hex}"
    result_json = json.dumps(result_payload, sort_keys=True)
    result_checksum = hashlib.sha256(result_json.encode("utf-8")).hexdigest()
    with connect(settings.database_path) as connection:
        provenance = connection.execute(
            """
            SELECT r.id, dv.id
            FROM regions AS r
            JOIN dataset_versions AS dv ON dv.id = r.source_dataset_version_id
            ORDER BY r.id LIMIT 1
            """
        ).fetchone()
        if provenance is None:
            raise HTTPException(status_code=503, detail="No prepared dataset is available")
        region_id, dataset_version_id = provenance
        scenario_cursor = connection.execute(
            """
            INSERT INTO scenarios (
                identifier, name, scenario_version, region_id,
                spatial_unit_profile, spatial_unit_version,
                parameters_json, assumptions_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scenario_identifier,
                "Controlled agricultural-to-built-up conversion",
                request.scenario_version,
                region_id,
                "request-candidate-unit",
                request.scenario_version,
                json.dumps(request.model_dump(), sort_keys=True),
                json.dumps(request.assumptions),
            ),
        )
        scenario_run_cursor = connection.execute(
            """
            INSERT INTO scenario_runs (
                scenario_id, dataset_version_id, simulator_version,
                validation_strategy, validation_version, status,
                started_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, 'completed', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (scenario_cursor.lastrowid, dataset_version_id, "simulator-v1", "deterministic", "v1"),
        )
        connection.execute(
            """
            INSERT INTO scenario_results (
                scenario_run_id, baseline_json, scenario_json, result_checksum
            ) VALUES (?, ?, ?, ?)
            """,
            (
                scenario_run_cursor.lastrowid,
                json.dumps(result.baseline_area_by_class, sort_keys=True),
                json.dumps(result.scenario_area_by_class, sort_keys=True),
                result_checksum,
            ),
        )
        write_audit(
            connection,
            event_type="SCENARIO_EXECUTED",
            user_id=user.id,
            entity_type="scenario_run",
            entity_id=str(scenario_run_cursor.lastrowid),
            details_json=json.dumps({"checksum": result_checksum}),
        )
    result_payload["scenario_identifier"] = scenario_identifier
    result_payload["result_checksum"] = result_checksum
    return result_payload


@app.post("/api/insights")
def insight(
    request: InsightRequest,
    user: AuthenticatedUser = Depends(require_roles("ADMIN", "POLICY_ANALYST", "RESEARCHER")),
) -> dict[str, Any]:
    provider = LlamaCppProvider(settings.llama_cpp_base_url, settings.llama_cpp_model)
    with connect(settings.database_path) as connection:
        evidence = search_evidence(connection, request.evidence_query, limit=10) if request.evidence_query else []
    result = build_grounded_insight(
        provider,
        question=request.question,
        evidence=evidence,
        scenario_result=request.scenario_result,
        assumptions=request.assumptions,
    ).as_dict()
    with connect(settings.database_path) as connection:
        write_audit(connection, event_type="AI_INSIGHT_REQUESTED", user_id=user.id)
    return result
