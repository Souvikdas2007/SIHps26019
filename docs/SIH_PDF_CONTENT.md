# SIH 2026 Presentation Content Mapping

## Slide 1 - Title

- **Problem Statement ID:** PS26019
- **Problem Statement Title:** National Digital Platform for Research, Policy Innovation, and Evidence-Based Land Governance
- **Theme:** Smart Automation
- **Category:** Software
- **Team ID:** `[VERIFY WITH TEAM]`
- **Team Name:** `[VERIFY WITH TEAM]`
- **Project:** PS26019
- **Positioning:** Offline-first evidence-to-decision prototype for land governance.

**Accuracy note:** The current implementation is a synthetic local MVP/demo. It must not be presented as a national deployment or as using official Kolkata/government datasets.

## Slide 2 - Idea

### Problem
Land-governance evidence, land-use observations, analytics and policy reasoning are often handled separately. The prototype demonstrates one connected workflow from a policy question to an explainable scenario result.

### Proposed solution
A local policy-intelligence workspace that combines:

1. SQLite-backed evidence search.
2. Observed land-use analytics.
3. A deterministic agricultural-to-built-up scenario simulator.
4. Optional local LLM explanation with an explicit offline fallback.

### USP
**Evidence -> Geography -> Analytics -> Simulation -> Decision Insight**, with numerical results owned by deterministic application code rather than the LLM.

### Main workflow
Policy question -> FTS5 evidence search -> synthetic study-area analytics -> configure weights -> run scenario -> inspect baseline/scenario values and affected unit IDs -> request explanation.

### Difference
The implemented prototype keeps evidence, observed facts, assumptions, simulated values and limitations visibly separated, and continues to work for core analytics/simulation when the local LLM is offline.

## Slide 3 - Technical Approach

### Actual technologies

- **Frontend:** React, TypeScript, Vite, CSS.
- **Backend:** Python, FastAPI, Pydantic, Uvicorn.
- **Database:** SQLite 3 with numbered migrations, foreign keys and SQLite FTS5.
- **GIS/data:** Dependency-free GeoJSON `FeatureCollection` importer; GeoJSON asset stored outside SQLite and metadata/observations stored in SQLite.
- **Simulation:** Python deterministic scoring, stable ranking, eligibility filtering and partial allocation.
- **AI:** Replaceable `LLMProvider` contract, llama.cpp HTTP adapter, GGUF model configuration.
- **RAG:** SQLite document/chunk metadata plus FTS5 lexical retrieval. No embeddings or hybrid ranking are implemented.

### Actual data flow

Seeded synthetic GeoJSON and synthetic policy chunks -> importer/indexer -> SQLite metadata, observations and FTS5 chunks -> evidence/analytics API -> request-supplied scenario candidates and visible weights -> deterministic result persistence -> optional grounded prompt to llama.cpp -> insight or explicit unavailable fallback.

### Actual architecture

React/Vite browser -> FastAPI modular monolith -> SQLite-backed evidence, analytics, auth/audit and scenario orchestration -> Python core modules -> optional local llama.cpp server. See `docs/sih_assets/system_architecture.md` and its SVG.

### Important boundary
The current browser “map” is a styled placeholder with layer controls and legend. MapLibre/Leaflet rendering, geometry inspection and affected-geometry rendering are not implemented.

## Slide 4 - Feasibility and Viability

### Working now

- Seeded synthetic database and GeoJSON demo asset.
- Source-attributed lexical evidence search.
- Deterministic land-use totals, percentages and period change.
- Authenticated scenario execution with role checks.
- Persisted scenario/run/result records and SHA-256 result checksum.
- Local scrypt password hashing, expiring sessions and audit events.
- Offline AI fallback that preserves deterministic results.
- Production frontend build and 11-test Python foundation suite pass.

### Existing data
One synthetic dataset/version, one synthetic region, three land-use observations, one synthetic document with three chunks, and one local GGUF model file are present in the workspace. They are demo fixtures, not official public data.

### Existing APIs
`/api/health`, `/api/auth/login`, `/api/evidence`, `/api/analytics`, `/api/scenarios/run`, `/api/insights`.

### Deployment approach
Single machine: Vite frontend, FastAPI backend, SQLite database, local processed assets and optional llama.cpp server.

### Risks and mitigations

- **LLM unavailable:** core evidence/analytics/simulation remain usable; UI reports unavailable insight.
- **Synthetic data:** label every demo result as synthetic and do not claim official provenance.
- **No real GIS rendering:** disclose placeholder and do not claim spatial impact geometry.
- **Lexical-only retrieval:** disclose FTS5-only implementation; do not claim semantic/hybrid search.
- **Missing production hardening:** disclose absent rate limiting, request-size controls and citation validation.

## Slide 5 - Impact and Benefits

### Target users
Policy analysts, researchers and land-governance teams are the intended future users; the current UI demonstrates their workflow with synthetic data.

### Expected benefits

- Traceable local evidence snippets.
- Reproducible what-if calculations.
- Visible assumptions, weights and limitations.
- Separation of observed analytics from simulated scenario values.
- Offline-capable core workflow after local setup.

### Governance, research and planning impact
The implemented pattern can support more transparent policy exploration once verified public datasets, study boundaries, geometry processing and stronger retrieval are added. These are expected benefits, not measured field outcomes of this prototype.

### Scalability/future potential
Documented future path: real bounded datasets, interactive GIS, persisted scenario history, PDF/HTML ingestion, local embeddings/hybrid retrieval, structured AI/citation validation and stronger security review. Do not claim these are implemented.

## Slide 6 - Research and References

### Data sources actually used

- No government or public dataset is used by the current seeded demo.
- `data/processed/synthetic-kolkata-lulc.geojson` is a synthetic fixture created by `scripts/seed_demo.py`.
- The indexed policy note is synthetic and stored through the seed script.
- The local model file is `models/local/SmolLM2-1.7B-Instruct-Q4_K_M.gguf`.

### Technical references represented in code

- Python standard library: SQLite, hashing, JSON, HTTP/client orchestration.
- FastAPI and Pydantic for HTTP API and validation.
- React, TypeScript and Vite for the frontend.
- SQLite FTS5 for lexical document retrieval.
- llama.cpp HTTP chat-completions adapter for optional local explanation.

### Project evidence
See the source files linked by `docs/SIH_PDF_PACKAGE.md`, especially `backend/app.py`, `core/evidence.py`, `core/analytics.py`, `core/simulation.py`, `ai/synthesis.py`, `scripts/seed_demo.py`, `tests/test_foundation.py`, and `Memory.md`.

### References requiring team verification
Verify the official SIH problem-statement metadata, team ID/name, final citation format, and any future government/public sources before submission.
