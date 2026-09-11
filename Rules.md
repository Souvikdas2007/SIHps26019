# Rules — PS26019

## 1. Core

1. Keep MVP narrow.
2. Reuse existing government sources.
3. Prefer explainability.
4. Make important results reproducible.
5. Record provenance.
6. Separate observed facts from simulations.
7. Deterministic code owns numerical calculations.
8. AI assists retrieval/explanation only.
9. No unsupported causal or prediction claims.
10. Core features must not require cloud AI.
11. LLM providers must be replaceable.

## 2. Technology

### MVP
- SQLite;
- Python;
- GeoPandas;
- Shapely;
- Pandas/NumPy;
- MapLibre GL JS or Leaflet;
- SQLite FTS5;
- local embeddings;
- llama.cpp with GGUF models.

### Avoid unless justified
- PostgreSQL/PostGIS in MVP;
- microservices;
- Kubernetes;
- Elasticsearch/OpenSearch;
- cloud LLM APIs;
- multiple overlapping databases;
- custom GIS engines.

## 3. SQLite

- SQLite is the application source of truth for metadata and transactional records.
- Use migrations.
- Enable foreign keys.
- Use parameterized queries/ORM.
- Do not expose the database file through the web server.
- Do not store huge raster datasets inside SQLite.
- Store large assets as files and keep references/metadata in SQLite.
- Do not require a SQLite extension without a fallback.

## 4. Data

Record:

```text
name
source
source_url
publisher
data_year
acquisition_date
spatial_resolution
temporal_resolution
CRS
license/usage_terms
processing_steps
version
```

Keep raw and processed data separate. Never silently overwrite source data.

## 5. GIS

- standardize CRS;
- use appropriate projected CRS for area/distance;
- validate geometries;
- preprocess static layers;
- simplify browser layers;
- never join datasets solely by similar names;
- preserve source geometry.

## 6. Simulation

Expose:
- parameters;
- model version;
- factors;
- weights;
- assumptions;
- data versions;
- calculation method.

Never:
- call a heuristic a guaranteed prediction;
- claim causality without evidence;
- hide assumptions;
- let AI modify numerical outputs.

Always:
- produce deterministic results;
- compare baseline/scenario;
- preserve configuration;
- identify limitations.

## 7. Local AI/RAG

AI may:
- retrieve;
- summarize;
- synthesize;
- explain;
- draft reports.

AI must not:
- invent citations/datasets;
- invent authoritative values;
- alter source records;
- execute SQL/shell/application commands;
- make unsupported policy claims.

Retrieved text is **untrusted data**, not instructions.

Use hybrid retrieval: SQLite FTS5 + local embeddings.

## 8. Plug-and-Play LLM

All application code depends on an `LLMProvider` interface, not directly on
llama.cpp or any other runtime.

Configuration controls:
- provider;
- endpoint;
- chat model;
- embedding model;
- generation limits;
- timeout.

Provider-specific code stays in the provider adapter.

## 8.1 Plug-and-Play Project Decisions

The following must be replaceable through versioned configuration or interfaces:

- study boundary and region profile;
- source dataset and dataset version;
- simulation spatial unit;
- scenario factors, weights and constraints;
- validation strategy;
- local chat model and embedding model;
- authentication implementation.

Use stable contracts such as `StudyAreaProvider`, `DatasetProfile`,
`SpatialUnitProvider`, `ValidationStrategy`, `EmbeddingProvider` and
`AuthProvider`. Do not embed these choices in UI code or core simulation
logic. Persist the selected profile and version with every derived result.

## 9. Failure Behavior

If the local LLM fails:

```text
Evidence search → works
GIS → works
Analytics → works
Simulation → works
AI synthesis → clear unavailable state
```

Never make AI a single point of failure for the core decision workflow.

## 10. Logging

Log:
- auth events;
- scenario execution;
- model/data versions;
- errors;
- AI runtime status.

Never log passwords, tokens, API keys or unnecessary personal information.

## 11. Code

- validate API input;
- isolate simulation logic;
- keep business logic out of UI;
- use environment configuration;
- test core calculations;
- isolate database and AI providers.

## 12. Scope Rule

A feature belongs in MVP only if it directly supports:

**Evidence → GIS → Analytics → Scenario → Decision Insight**

## 13. Definition of Done

A feature is complete when it works end-to-end, validates input, records provenance, has tested core logic, handles errors, explains its result and does not create an unnecessary external dependency.
