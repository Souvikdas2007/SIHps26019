CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT,
    publisher TEXT,
    license_terms TEXT,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dataset_versions (
    id INTEGER PRIMARY KEY,
    dataset_id INTEGER NOT NULL REFERENCES datasets(id),
    version TEXT NOT NULL,
    data_year INTEGER,
    acquisition_date TEXT,
    spatial_resolution TEXT,
    temporal_resolution TEXT,
    crs TEXT,
    processing_steps TEXT NOT NULL DEFAULT '',
    asset_path TEXT NOT NULL,
    checksum TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dataset_id, version)
);

CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY,
    identifier TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    profile_version TEXT NOT NULL,
    source_dataset_version_id INTEGER REFERENCES dataset_versions(id),
    geometry_path TEXT,
    crs TEXT,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT,
    publisher TEXT,
    publication_date TEXT,
    document_type TEXT,
    license_terms TEXT,
    file_path TEXT NOT NULL,
    checksum TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_reference TEXT,
    UNIQUE(document_id, chunk_index)
);

CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts USING fts5(
    content,
    source_id UNINDEXED,
    document_chunk_id UNINDEXED
);

CREATE TABLE IF NOT EXISTS landuse_observations (
    id INTEGER PRIMARY KEY,
    dataset_version_id INTEGER NOT NULL REFERENCES dataset_versions(id),
    region_id INTEGER NOT NULL REFERENCES regions(id),
    spatial_unit_id TEXT NOT NULL,
    observed_year INTEGER NOT NULL,
    land_use_class TEXT NOT NULL,
    area_sq_m REAL NOT NULL CHECK (area_sq_m >= 0),
    geometry_path TEXT,
    UNIQUE(dataset_version_id, region_id, spatial_unit_id, observed_year, land_use_class)
);

CREATE TABLE IF NOT EXISTS analytics_results (
    id INTEGER PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    dataset_version_id INTEGER NOT NULL REFERENCES dataset_versions(id),
    profile_version TEXT NOT NULL,
    result_type TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY,
    identifier TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    scenario_version TEXT NOT NULL,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    spatial_unit_profile TEXT NOT NULL,
    spatial_unit_version TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    assumptions_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenario_runs (
    id INTEGER PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
    dataset_version_id INTEGER NOT NULL REFERENCES dataset_versions(id),
    simulator_version TEXT NOT NULL,
    validation_strategy TEXT NOT NULL,
    validation_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS scenario_results (
    id INTEGER PRIMARY KEY,
    scenario_run_id INTEGER NOT NULL REFERENCES scenario_runs(id) ON DELETE CASCADE,
    baseline_json TEXT NOT NULL,
    scenario_json TEXT NOT NULL,
    affected_geometry_path TEXT,
    result_checksum TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY,
    provider TEXT NOT NULL,
    runtime TEXT NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    model_format TEXT NOT NULL,
    asset_path TEXT,
    checksum TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, runtime, model_name, model_version)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO roles (name, description) VALUES
    ('ADMIN', 'System administrator'),
    ('POLICY_ANALYST', 'Can analyze evidence and run scenarios'),
    ('RESEARCHER', 'Can manage research evidence'),
    ('VIEWER', 'Can view published results');
