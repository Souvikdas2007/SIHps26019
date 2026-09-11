# Architecture — PS26019 MVP

## 1. Strategy

Use a **modular monolith + Python geospatial/simulation modules + local AI/RAG runtime**.

No microservices are required for the MVP.

## 2. High-Level Architecture

```text
                         USER
                           |
                           v
                    WEB FRONTEND
                 Search | GIS | KPI
                 Scenario | Insights
                           |
                       REST/JSON
                           |
                           v
                    BACKEND API
          Auth | Evidence | Analytics | Scenarios
                    Audit | AI orchestration
                    /                 \
                   /                   \
                  v                     v
             SQLITE DB            LOCAL AI/RAG
          metadata/results        Retrieval + LLM
                  |                     |
                  v                     v
      Python Geo Processing     llama.cpp / Local LLM
        GeoPandas + Shapely
                  |
                  v
          SIMULATION ENGINE
     Eligibility | Scoring | Allocation
                  |
                  v
        Metrics + Simplified GeoJSON
```

## 3. Frontend

Responsibilities:
- evidence search;
- GIS/layers;
- analytics;
- scenario controls;
- result comparison;
- AI insight.

Use the team's existing frontend stack. React/Next.js is suitable if already known.

GIS: MapLibre GL JS or Leaflet.

## 4. Backend

Responsibilities:
- authentication/authorization;
- metadata;
- evidence retrieval;
- analytics;
- scenario orchestration;
- result persistence;
- audit;
- local AI orchestration.

Example APIs:

```text
/api/auth
/api/evidence
/api/documents
/api/datasets
/api/regions
/api/analytics
/api/scenarios
/api/scenarios/{id}/run
/api/scenarios/{id}/results
/api/insights
/api/ai/health
```

## 5. SQLite Database

Suggested tables:

```text
users
roles
documents
document_chunks
datasets
dataset_versions
regions
landuse_observations
analytics_results
scenarios
scenario_runs
scenario_results
model_versions
audit_logs
```

SQLite stores application metadata and transactional records.

### Spatial strategy

SQLite does not provide PostGIS functionality by default. Therefore:
- store small geometry payloads as GeoJSON/WKB where useful;
- keep large geospatial layers in GeoJSON/GeoPackage/files;
- store file/version metadata in SQLite;
- use GeoPandas/Shapely for spatial operations;
- return simplified GeoJSON to the frontend.

Optional extensions such as SpatiaLite or sqlite-vec may be evaluated later, but are not mandatory.

## 6. Local RAG

```text
Documents
   ↓
Text extraction
   ↓
Chunking
   ↓
SQLite metadata + FTS5
   +
Local embeddings
   ↓
Hybrid retrieval
   ↓
Evidence filtering
   ↓
Prompt builder
   ↓
Local LLM
   ↓
Grounded insight
```

SQLite FTS5 provides lexical retrieval. A replaceable vector adapter provides semantic retrieval. The MVP may use sqlite-vec when available or a small local vector index referenced by SQLite.

## 7. LLM Provider Interface

```python
class LLMProvider:
    def generate(self, prompt: str, context: dict) -> str:
        raise NotImplementedError

    def health(self) -> bool:
        raise NotImplementedError
```

Default:

```text
LLMProvider
   └── LlamaCppProvider
```

Future local or cloud adapters can implement the same interface, for example
`OpenAIProvider` or `GeminiProvider`. Business logic must depend only on
`LLMProvider`.

Example configuration:

```text
LLM_PROVIDER=local
LLM_RUNTIME=llama.cpp
LLAMA_CPP_BASE_URL=http://127.0.0.1:8080
LLAMA_CPP_MODEL=<local-chat-model>.gguf
EMBEDDING_MODEL=<local-embedding-model>
```

## 8.1 Plug-and-Play Decision Profiles

Unresolved preparation choices are selected through versioned profiles and
replaceable interfaces:

```text
StudyAreaProvider       → Kolkata study-area profile
DatasetProfile           → prepared dataset versions
SpatialUnitProvider      → grid, parcel or administrative unit
ScenarioConfig           → factors, weights and constraints
ValidationStrategy       → selected reproducibility/quality checks
EmbeddingProvider        → local embedding implementation
AuthProvider             → local authentication implementation
```

The API and UI consume the common profile contracts rather than knowing which
specific boundary, dataset, spatial unit, model or validation strategy was
selected. Profile identifiers and versions are persisted with scenario runs,
analytics results and AI context.

## 8. Geospatial Processing

Preprocess static layers.

Operations:
- CRS transformation;
- clipping;
- geometry repair;
- spatial joins;
- buffers;
- intersections;
- area;
- aggregation;
- proximity.

## 9. Simulation

Deterministic for identical dataset versions, study area, parameters and model version.

Example:

```text
Score =
    w1 * UrbanProximity
  + w2 * PopulationPressure
  + w3 * InfrastructureAccess
  - w4 * EnvironmentalConstraint
```

Pipeline:

```text
Parameters
 ↓
Eligible agricultural features
 ↓
Factors
 ↓
Normalization
 ↓
Suitability score
 ↓
Ranking
 ↓
Allocation
 ↓
Impact metrics
 ↓
Affected geometry
```

## 10. AI Guardrails

The local LLM:
- receives evidence as data, not instructions;
- cannot execute SQL/shell commands;
- cannot modify simulation results;
- must use retrieved source IDs;
- must distinguish observed and simulated results.

If the local model is unavailable, Evidence, GIS, Analytics and Simulation remain usable.

## 11. Project Structure

```text
ps26019/
├── frontend/
├── backend/
│   ├── auth/
│   ├── evidence/
│   ├── datasets/
│   ├── analytics/
│   ├── scenarios/
│   ├── ai/
│   └── audit/
├── core/
│   ├── database/
│   │   ├── sqlite/
│   │   └── migrations/
│   ├── geospatial/
│   └── simulation/
├── ai/
│   ├── providers/
│   │   ├── base.py
│   │   └── llama_cpp.py
│   ├── embeddings/
│   ├── retrieval/
│   ├── prompts/
│   └── synthesis/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── documents/
│   └── metadata/
├── storage/
│   └── ps26019.db
├── tests/
└── docs/
```

## 12. Deployment

Single-machine MVP:

```text
Frontend + Backend + Python
        |
      SQLite
        |
 Local LLM Runtime (llama.cpp)
        |
 Local processed datasets
```

This enables an offline/local demonstration after required models and datasets are prepared.

## 13. Scaling Path

Later:
- PostgreSQL/PostGIS migration;
- object storage;
- vector database;
- asynchronous jobs;
- tile services;
- model registry;
- national-scale ingestion.

Keep database and AI access behind interfaces so these migrations do not rewrite the product workflow.
