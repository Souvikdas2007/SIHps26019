# PS26019 Project Memory

> This file is the primary technical handover for future AI agents. Read this file first, then inspect only the files relevant to the requested change. The repository currently contains a working synthetic offline MVP/demo, not a production national data deployment.

## 1. Project Identity

**Project:** PS26019 / SIH26019
**Title:** National Digital Platform for Research, Policy Innovation, and Evidence-Based Land Governance
**Goal:** Connect local policy/research evidence, land-use geography, deterministic analytics, scenario simulation and explainable AI into one decision workflow.
**USP:** Evidence -> Geography -> Analytics -> Simulation -> Decision Insight.

## 2. Non-Negotiable Product Decisions

Do not change these without explicit user discussion:

- Offline-first after installation, data preparation and model preparation.
- SQLite is the MVP primary/source-of-truth database. Do not replace it with PostgreSQL/PostGIS for MVP.
- Local AI is the default. The local LLM runtime is llama.cpp with a GGUF model.
- Business logic depends on replaceable provider/profile contracts, not directly on a model runtime.
- Code performs authoritative numerical calculations, GIS operations and simulation. AI explains supplied results.
- Cloud LLMs are optional and must never be required for the MVP.
- The MVP focuses on one workflow: policy question -> evidence -> region -> GIS/history -> analytics -> scenario -> simulation -> comparison -> affected areas -> AI insight.
- Demonstration scenario: controlled agricultural-to-built-up conversion around an expanding urban area.
- Demonstration geography: Kolkata / peri-urban West Bengal.
- Synthetic data is acceptable for local regression/demo testing, but must never be presented as official government data.
- Avoid microservices, Kubernetes, nationwide data, black-box prediction and unnecessary infrastructure.

## 3. Current Status

**Current phase:** Phase 7 Security + Review, partially completed.
**Overall status:** Synthetic offline MVP workflow is runnable and testable. Production data, interactive GIS rendering, semantic embeddings and final security hardening remain.
**Backend:** Implemented and runnable.
**Frontend:** Implemented as a React/Vite single-page policy workspace with interactive navigation and controls.
**Local AI:** llama.cpp + SmolLM2 GGUF has been tested successfully through the chat-completions endpoint.

## 4. Technology Stack

- Frontend: React, TypeScript, Vite, CSS.
- Backend: Python 3.11+, FastAPI, Pydantic, Uvicorn.
- Database: SQLite 3 with numbered migrations, foreign keys and SQLite FTS5.
- Data/GIS libraries declared: Pandas, NumPy, GeoPandas, Shapely, PyProj.
- Spatial assets: GeoJSON/GeoPackage/GeoTIFF files outside SQLite; SQLite stores metadata, paths, versions and derived records.
- Local LLM: llama.cpp server, GGUF model.
- Default tested model: `SmolLM2-1.7B-Instruct-Q4_K_M.gguf`.
- Retrieval currently implemented: SQLite FTS5 lexical retrieval. Local semantic embeddings/hybrid ranking are not implemented yet.

## 5. Repository Map

```text
PS26019_Project_Documentation_v2/
├── backend/
│   ├── app.py                 # FastAPI routes and orchestration
│   ├── config.py              # Environment-driven Settings
│   └── security.py            # Password hashing, sessions, roles, audit helper
├── core/
│   ├── analytics.py           # Deterministic land-use summaries
│   ├── evidence.py            # SQLite FTS5 document indexing/search
│   ├── profiles.py            # Replaceable profile/provider protocols
│   ├── simulation.py          # Deterministic scenario engine
│   ├── data/catalog.py        # Small prepared GeoJSON registration/import
│   └── database/
│       ├── connection.py      # SQLite connection + foreign keys
│       ├── migrator.py        # Idempotent numbered migration runner
│       └── migrations/        # 001, 002 and 003 schema migrations
├── ai/
│   ├── providers/base.py      # LLMProvider protocol and availability type
│   ├── providers/llama_cpp.py # llama.cpp chat-completions adapter
│   └── synthesis.py           # Grounded insight orchestration/fallback
├── frontend/
│   ├── src/main.tsx           # Current complete React workspace UI
│   ├── src/CatalogModule.tsx  # Dataset and local-model catalog UI
│   ├── src/styles.css         # Visual system and responsive interaction CSS
│   ├── package.json            # Vite/React build commands
│   └── vite.config.ts
├── scripts/
│   ├── init_database.py       # Apply SQLite migrations
│   ├── seed_demo.py           # Seed clearly labeled synthetic demo data
│   └── create_admin.py        # Create/update local admin from env credentials
├── Makefile                   # Cross-command setup, checks and local service runner
├── tests/test_foundation.py   # Current 12-test regression suite
├── database/ps26019.db       # Local SQLite database, ignored by Git
├── data/processed/            # Synthetic GeoJSON demo asset
├── models/local/              # Local GGUF models, ignored by Git
├── .env.example
├── requirements.txt
├── README.md
└── project documentation markdown files
```

## 6. Database and Migrations

Default database path:

```text
database/ps26019.db
```

Migrations:

- `001_initial.sql`: roles, users, datasets, dataset versions, regions, documents, chunks, FTS5 table, observations, analytics results, scenarios, scenario runs/results, model versions and audit logs.
- `002_dataset_profile_identifier.sql`: persists `datasets.profile_identifier`.
- `003_security_sessions.sql`: adds hashed-token `auth_sessions` and expiry index.

Important tables:

```text
roles, users
sessions: auth_sessions
documents, document_chunks, document_chunks_fts
datasets, dataset_versions, regions
landuse_observations, analytics_results
scenarios, scenario_runs, scenario_results
model_versions, audit_logs
```

SQLite behavior:

- Every connection enables `PRAGMA foreign_keys = ON`.
- Migrations are idempotent and tracked in `schema_migrations`.
- Large spatial files are not stored inside SQLite.
- The database file must not be served publicly.

## 7. Synthetic Demo Data

Run:

```bash
.venv/bin/python scripts/seed_demo.py
```

The seed creates/registers:

- `data/processed/synthetic-kolkata-lulc.geojson`
- Dataset profile `synthetic-kolkata-lulc`, version `demo-v1`.
- Region profile `synthetic-kolkata-peri-urban`, version `demo-v1`.
- Three land-use observations across synthetic units/years.
- One synthetic evidence document, source ID `synthetic-policy-001`, with three chunks.

The synthetic dataset is only a test/demo fixture. Do not call it official Kolkata, government or research data.

## 8. Backend API Contract

Base URL during local development:

```text
http://127.0.0.1:8000
```

Endpoints currently implemented:

- `GET /api/health`: SQLite and llama.cpp availability.
- `POST /api/auth/login`: accepts username/password and returns bearer token.
- `GET /api/evidence?query=...&limit=...`: local FTS5 search with source ID/title/snippet.
- `GET /api/analytics`: deterministic land-use totals, percentages and changes.
- `GET /api/catalog`: authenticated inventory of registered datasets and models.
- `POST /api/catalog/datasets`: ADMIN/RESEARCHER registration of an existing project-local GeoJSON LULC asset.
- `POST /api/catalog/models`: ADMIN registration of local model metadata and an optional existing model asset path.
- `POST /api/scenarios/run`: protected; validates request, runs deterministic simulator, persists scenario/run/result and audit event.
- `POST /api/insights`: protected; retrieves evidence, calls LLM provider and returns grounded/unavailable insight.

Protected routes use:

```text
Authorization: Bearer <access_token>
```

Roles:

- `ADMIN` and `POLICY_ANALYST`: scenario execution.
- `ADMIN`, `POLICY_ANALYST` and `RESEARCHER`: insight requests.
- `VIEWER`: authenticated viewing only; scenario execution returns 403.

## 9. Authentication and Security

Password handling:

- Passwords are stored as salted `scrypt$...` hashes.
- Plaintext passwords are never written to SQLite.
- Sessions store SHA-256 token hashes, not raw bearer tokens.
- Sessions expire after the configured default of 8 hours.

Create an admin from a shell, never by putting credentials in source:

```bash
export PS26019_ADMIN_USERNAME=admin
export PS26019_ADMIN_PASSWORD='use-a-password-at-least-12-chars'
.venv/bin/python scripts/create_admin.py
```

Audit events currently include login success/failure, authorization denied, scenario execution and AI insight requests.

Still incomplete:

- Rate limiting.
- Request-size limits.
- Upload security, because uploads are not enabled.
- Fine-grained permissions beyond protected route roles.
- Full dependency/security audit.
- Structured AI output and citation validation.

## 10. Frontend Behavior

Frontend URL:

```text
http://localhost:5173
```

The frontend is a single-page workspace, not separate routes. Navigation scrolls to these real sections and highlights the active section:

- Workspace: policy question overview.
- Evidence: FTS5 search and source snippets.
- Geography: observed analytics and map/layer surface.
- Scenarios: requested area, four weights, simulation and result display.
- Decision Insight: AI result, limitations, affected units and recent local runs.

Existing interactive behavior:

- Login/logout with localStorage bearer token.
- Evidence search calls `/api/evidence`.
- Refresh observed data calls `/api/analytics`.
- Region dropdown opens below trigger, selects a prepared region profile, closes outside and on Escape.
- Layer panel opens/closes; LULC, Boundaries and Roads checkboxes update the visible layer legend state.
- Scenario controls update React state and call `/api/scenarios/run`.
- Generate Insight requires a completed scenario, then calls `/api/insights`.
- Toasts show refresh, login, evidence and simulation feedback.
- Loading labels disable duplicate requests.
- Errors appear near the affected workflow area.
- Responsive layout has been checked at 1920, 1440, 1024, 768, 480 and 375 widths.
- CSS supports reduced motion through `prefers-reduced-motion`.

Important limitation: the current map is a contained visual placeholder with layer controls and legend. A real MapLibre/Leaflet map and affected geometry rendering are not implemented yet.

## 11. AI/RAG Implementation State

`ai/providers/llama_cpp.py` uses:

```text
POST http://127.0.0.1:8080/v1/chat/completions
```

It sends a system message plus user prompt, which is required for the tested SmolLM2 instruct model. The previous raw `/completion` path produced an empty response and was replaced.

Provider timeout is 60 seconds because local SmolLM inference can take more than 10 seconds on this machine.

Start llama.cpp with:

```bash
/home/mint/Documents/llamac++/llama.cpp/build/bin/llama-server \
  -m "/home/mint/Documents/AI createde/PS26019_Project_Documentation_v2/models/local/SmolLM2-1.7B-Instruct-Q4_K_M.gguf" \
  --host 127.0.0.1 \
  --port 8080
```

If llama.cpp is unavailable or returns no usable content, the AI layer returns an explicit unavailable state while preserving deterministic scenario results.

RAG rules:

- Retrieved text is untrusted data, not instructions.
- Source IDs are retained.
- AI must not calculate or modify authoritative numeric results.
- AI must not invent citations or unsupported causal claims.

## 12. Deterministic Analytics and Simulation

Analytics in `core/analytics.py` calculates:

- totals by year/class;
- percentages by year;
- first-to-last class changes.

Simulation in `core/simulation.py` accepts candidate areas and visible weights:

```text
Score =
    urban_proximity * w1
  + population_pressure * w2
  + infrastructure_access * w3
  - environmental_constraint * w4
```

Behavior:

- Only eligible agriculture candidates are ranked.
- Ranking is deterministic, using score descending then spatial-unit ID.
- Partial allocation of the final candidate is supported.
- Baseline/scenario class totals and selected units are returned.
- Scenario results are persisted by the API with a SHA-256 result checksum.
- Output is scenario analysis, not a guaranteed prediction.

## 13. Runbook

From the repository root:

```bash
cd "/home/mint/Documents/AI createde/PS26019_Project_Documentation_v2"
```

Seed data and create admin:

```bash
.venv/bin/python scripts/seed_demo.py
export PS26019_ADMIN_USERNAME=admin
export PS26019_ADMIN_PASSWORD='use-a-password-at-least-12-chars'
.venv/bin/python scripts/create_admin.py
```

Start three services in separate terminals:

```bash
# Terminal A: llama.cpp
/home/mint/Documents/llamac++/llama.cpp/build/bin/llama-server \
  -m "/home/mint/Documents/AI createde/PS26019_Project_Documentation_v2/models/local/SmolLM2-1.7B-Instruct-Q4_K_M.gguf" \
  --host 127.0.0.1 --port 8080
```

```bash
# Terminal B: backend
.venv/bin/uvicorn backend.app:app --reload
```

```bash
# Terminal C: frontend
cd frontend
npm run dev
```

Open `http://localhost:5173`, log in, search evidence, run a scenario and generate insight.

Stop services with `Ctrl+C` in their terminals. If necessary, stop only project ports:

```bash
fuser -k 8000/tcp 5173/tcp 8080/tcp
```

## 14. Testing and Verification

The root `Makefile` automates environment setup, dependency installation, database
initialization, demo seeding, service startup and verification. Use `make help`
for the complete command list; `make run` starts backend plus frontend, while
`make run-all` additionally starts llama.cpp when its local assets are available.

Current verified checks:

```bash
python3 -m unittest discover -s tests -v
```

Expected current result: **12 tests pass**.

```bash
cd frontend
npm run build
```

Expected: Vite production build passes.

Additional verified behavior:

- SQLite migrations apply safely and rerun with zero pending migrations.
- Synthetic ingestion records profile, version, CRS and SHA-256 checksum.
- FTS5 returns source-attributed snippets.
- Scenario execution is deterministic and persists records.
- Unauthenticated scenario access returns 401.
- Viewer scenario access returns 403.
- Admin/policy analyst scenario access returns 200.
- CORS preflight from `http://localhost:5173` returns 200.
- Production configuration rejects wildcard and non-HTTPS CORS origins.
- API responses include baseline browser security headers; HSTS is enabled in production mode.
- `/api/health` reports SQLite connected and llama.cpp available when server is running.
- Direct SmolLM chat completion returns grounded text.
- Responsive browser checks show no horizontal overflow at 375, 480, 768, 1024, 1440 and 1920 widths.

## 15. Known Limitations

- Only synthetic local data is currently available.
- Exact official Kolkata boundary and official source datasets remain undecided.
- The frontend map is a placeholder, not a real interactive GIS map.
- Dataset/model catalog registration is metadata and prepared-asset registration; browser uploads are intentionally not enabled.
- No GeoPandas/Shapely production geometry pipeline is connected to the UI yet.
- No PDF/HTML document ingestion pipeline exists.
- No local embedding model or semantic/hybrid retrieval exists.
- Scenario API persists results, but the frontend recent-runs list is session-local only.
- AI structured-output schema and citation validation are not implemented.
- Rate limiting, upload security and full dependency review remain.
- Current application is MVP/demo-ready, not production-ready for national deployment.

## 16. Correct Next Phase

Recommended next work, in order:

1. Replace the synthetic map placeholder with a real MapLibre GL JS or Leaflet map using the existing GeoJSON asset.
2. Render actual LULC and affected-unit layers without changing simulation calculations.
3. Add a persisted scenario-history GET endpoint and connect the frontend recent-runs view.
4. Add official dataset/study-area profiles only after source, CRS, license, version and checksum are documented.
5. Add PDF/text ingestion and local embeddings behind replaceable interfaces.
6. Add structured AI output validation and citation verification.
7. Add rate limiting and complete the Phase 7 security review.

## 17. Future AI Operating Rules

Before editing:

1. Read this `Memory.md`.
2. Read the relevant section of `Phases.md`.
3. Inspect only the owning files for the requested behavior.
4. Check whether the request changes a non-negotiable decision.
5. State one local hypothesis and one focused validation check.
6. Make the smallest change that tests the hypothesis.
7. Run focused validation immediately after editing.

Never:

- silently replace SQLite, llama.cpp, GGUF or offline-first behavior;
- invent official data, model results or citations;
- move numerical calculation into the LLM or frontend;
- bypass authentication to make the UI appear functional;
- claim the synthetic fixture is official data;
- mark a phase complete when its remaining items are listed here as incomplete.

## 18. Handover Summary

PS26019 is a working synthetic offline evidence-to-decision MVP.

Working now:

- SQLite migrations and provenance schema.
- Synthetic dataset/document seeding.
- FTS5 evidence search.
- Deterministic analytics.
- Deterministic agricultural-to-built-up scenario simulation.
- Scenario persistence and audit events.
- Local scrypt authentication and role checks.
- FastAPI health, evidence, analytics, scenario and insight endpoints.
- llama.cpp/SmolLM2 grounded explanation path.
- Interactive React/Vite frontend with navigation, dropdown, layer controls, loading/error/toast states and responsive layout.

Not complete:

- Official Kolkata datasets and bounded study boundary.
- Real interactive GIS map and geometry rendering.
- Semantic embeddings/hybrid retrieval.
- Structured AI/citation validation.

## SIH PDF Preparation Status

### Project State

The project is a working synthetic offline evidence-to-decision MVP/demo. The verified implemented path is React/Vite frontend -> FastAPI API -> SQLite/FTS5 and Python analytics/simulation -> optional llama.cpp explanation. The browser map is a styled placeholder, retrieval is lexical FTS5 only, and the seeded data is synthetic.

### PDF Assets Created

- `docs/SIH_PDF_CONTENT.md`
- `docs/SIH_PDF_PACKAGE.md`
- `docs/sih_assets/IMPLEMENTATION_STATUS.md`
- `docs/sih_assets/system_architecture.md`
- `docs/sih_assets/system_architecture.svg`
- `docs/sih_assets/data_flow.md`
- `docs/sih_assets/application_workflow.md`
- `docs/sih_assets/ai_rag_architecture.md`
- `docs/sih_assets/ai_rag_pipeline.md`
- `docs/sih_assets/scenario_simulation_pipeline.md`
- `docs/sih_assets/before_after_workflow.md`
- `docs/sih_assets/project_metrics.json`
- `docs/sih_assets/project_metrics.md`
- `docs/sih_assets/demo_results.md`
- Real browser screenshots under `docs/sih_assets/`.

### Verified Features

- Seeded synthetic GeoJSON and synthetic policy chunks.
- SQLite migrations, foreign keys, metadata, observations, scenarios and audit records.
- Source-attributed FTS5 evidence search.
- Deterministic land-use analytics.
- Deterministic agricultural-to-built-up scenario scoring, ranking and partial allocation.
- Protected scenario/insight routes with local scrypt authentication and roles.
- Scenario persistence with result checksum.
- Grounded llama.cpp adapter and explicit offline fallback.
- Live browser flow: login -> evidence -> analytics -> scenario -> result -> AI fallback.

### Verified Metrics

At capture time: 6 API routes, 3 migrations, 1 dataset, 1 dataset version, 1 region, 3 land-use observations, 1 document, 3 indexed chunks, 4 roles, 11 passing foundation tests, and `llm_available: false`. See `docs/sih_assets/project_metrics.json`; mutable database counts must be rechecked before submission.

### Screenshots

Real screenshots captured from the running Vite application are listed in `docs/SIH_PDF_PACKAGE.md`, including workspace, evidence, geography/KPI placeholder, historical analytics, scenario configuration/result, and AI offline fallback.

### Architecture

The presentation architecture is intentionally limited to the actual modular monolith: React/Vite, FastAPI, SQLite/FTS5, Python importer/analytics/simulation, file-based GeoJSON and optional llama.cpp/GGUF. The SVG and Mermaid diagrams explicitly disclose the missing browser GIS renderer.

### Demo Workflow

The verified run searched `agricultural conversion`, displayed seeded analytics, authenticated as a local admin, ran the default `9000 m²` scenario with four weights, selected `unit-001`, returned `15000 m²` agriculture and `9000 m²` built-up in the scenario, and displayed the local AI unavailable fallback.

### Known Limitations

- Synthetic-only data and synthetic evidence.
- No real interactive map or affected geometry rendering.

## 19. Phase 9 Frontend Modernization

The frontend is now a routed React application rather than a single scrolling workspace.

Routes:

- `/dashboard`
- `/evidence`
- `/geography`
- `/analytics`
- `/scenarios`
- `/insights`
- `/data`
- `/settings`

Implementation:

- `frontend/src/App.tsx` owns the application shell, sidebar navigation, responsive drawer, route views, session state and workflow state.
- `frontend/src/services/api.ts` centralizes typed requests for health, login, evidence, analytics, catalog, scenarios and insights.
- `frontend/src/types.ts` contains shared frontend response types.
- The existing bearer-token authentication flow remains in place; protected scenario, insight and catalog APIs are never bypassed.
- The map remains explicitly labelled as a GeoJSON-ready placeholder because browser geometry rendering is not implemented.
- Synthetic values and simulated outputs are labelled separately from observed/source-derived data.
- `react-router-dom` was added as the only frontend runtime dependency.
- `frontend/src/styles.css` now provides the policy-intelligence shell, page hierarchy, responsive breakpoints, drawer navigation, loading/error/empty visual states, map surface, tables, controls and reduced-motion behavior.

Validation performed:

- `cd frontend && npm run build` passes after the modernization.

Remaining frontend work:

- Add a real MapLibre or Leaflet renderer and affected geometry layer.
- Add richer skeleton/loading states and persisted scenario history.
- Run live browser checks against the backend at all target viewport sizes after the next visual iteration.
- No PDF/HTML extraction, embeddings or hybrid retrieval.
- No structured AI output/citation validation.
- Local LLM was offline during asset capture.
- No rate limiting/request-size controls or full dependency audit.
- Several target capabilities in PRD/architecture documents remain planned.

### Pending Work

Before final SIH submission, verify team metadata and official references, recheck mutable metrics, decide whether to run llama.cpp in the final demo, and keep all claims aligned with `IMPLEMENTATION_STATUS.md`.

### Important Context for Future AI

Treat `docs/SIH_PDF_PACKAGE.md`, `docs/SIH_PDF_CONTENT.md` and `docs/sih_assets/` as the evidence-backed submission handover. Do not upgrade planned MapLibre/Leaflet, embedding, official-data, citation-validation or national-scale claims into implemented features. Re-run the live workflow and refresh `project_metrics.json` if the local database changes.
- Rate limiting, upload controls and complete security review.

A new AI should use this file as the project map and start with the **Correct Next Phase** section rather than rereading the entire codebase.
