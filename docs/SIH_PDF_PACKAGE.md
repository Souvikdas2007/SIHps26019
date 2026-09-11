# SIH PDF PACKAGE

This package describes the actual implementation captured from the workspace on 2026-09-11. Synthetic/demo values are labeled as such. Team metadata and final official references require manual verification.

## Slide 1

**PS26019 — National Digital Platform for Research, Policy Innovation, and Evidence-Based Land Governance**

- Theme: Smart Automation.
- Category: Software.
- Team ID: `[VERIFY WITH TEAM]`.
- Team name: `[VERIFY WITH TEAM]`.
- Positioning: Offline-first evidence-to-decision prototype for land governance.

Do not claim national deployment, official Kolkata data or authoritative prediction.

## Slide 2

**From scattered evidence to an explainable policy what-if.**

- Problem: policy evidence, land-use observations and scenario reasoning are disconnected.
- Solution: local evidence search, observed analytics, deterministic scenario simulation and optional local AI explanation in one workspace.
- USP: Evidence -> Geography -> Analytics -> Simulation -> Decision Insight.
- Workflow: question -> FTS5 evidence -> observed KPIs -> weights -> simulation -> result/limitations -> insight/fallback.
- Difference: deterministic code owns numerical results; AI explains supplied context only.

## Slide 3

**Actual technical approach**

- Frontend: React + TypeScript + Vite + CSS.
- Backend: Python + FastAPI + Pydantic + Uvicorn.
- Database: SQLite 3 + numbered migrations + foreign keys + FTS5.
- GIS/data: small prepared GeoJSON importer and file-based GeoJSON asset; no browser GIS renderer.
- Analytics/simulation: Python deterministic modules.
- AI/RAG: `LLMProvider`, llama.cpp HTTP adapter, GGUF configuration, SQLite FTS5 lexical retrieval.
- Data flow: seed synthetic assets -> validate/index -> SQLite -> evidence/analytics -> scenario API -> persisted result -> optional llama.cpp explanation.

See [system_architecture.md](sih_assets/system_architecture.md), [system_architecture.svg](sih_assets/system_architecture.svg) and [data_flow.md](sih_assets/data_flow.md).

## Slide 4

**Feasibility and viability**

Working: local seed, evidence search, analytics, authenticated simulation, persistence/audit, frontend build, deterministic tests and AI offline fallback.

Data: one synthetic dataset/version, one region, three observations, one synthetic document with three chunks, and one local GGUF file.

APIs: health, login, evidence, analytics, scenario run and insights.

Deployment: Vite + FastAPI + SQLite + local files + optional llama.cpp on one machine.

Risks: synthetic-only data, placeholder map, lexical-only retrieval, optional/offline LLM, absent citation validation and incomplete hardening. Mitigations are explicit labeling, deterministic calculations, input validation, role checks, audit records and offline fallback.

## Slide 5

**Impact and benefits**

- Future target users: policy analysts, researchers and land-governance teams.
- Current demonstrated benefits: source-attributed snippets, reproducible what-if values, visible assumptions/weights/limitations, observed vs simulated separation and local core operation without cloud AI.
- Governance/research/planning relevance: creates a transparent workflow that can accept verified public datasets in a future phase.
- Scalability path: interactive GIS, official dataset profiles, document extraction, embeddings/hybrid retrieval, structured AI validation and production hardening.

These are intended benefits and future potential, not measured field outcomes.

## Slide 6

**Research and references**

- Actual demo data: synthetic GeoJSON and synthetic policy chunks from `scripts/seed_demo.py`; no government/public source is used in the seeded demo.
- Technical implementation: Python, FastAPI, Pydantic, React, TypeScript, Vite, SQLite FTS5 and llama.cpp adapter.
- Primary project evidence: `backend/app.py`, `core/evidence.py`, `core/analytics.py`, `core/simulation.py`, `ai/synthesis.py`, `scripts/seed_demo.py`, `tests/test_foundation.py`, `Memory.md`.
- Manual verification required: official SIH metadata, team information, approved public/government references, licenses and any claims about actual deployment or coverage.

## Screenshots

All screenshots were captured from the running Vite frontend at `http://127.0.0.1:5173/` after seeding the local SQLite database.

- `sih_assets/dashboard_workspace.png` — full workspace with seeded analytics and controls.
- `sih_assets/evidence_explorer.png` — actual FTS5 search result for `agricultural conversion`.
- `sih_assets/geography_gis_placeholder.png` — actual Geography panel; demonstrates KPI/layer surface and explicitly shows the placeholder map.
- `sih_assets/historical_analytics.png` — actual historical KPI values.
- `sih_assets/scenario_configuration.png` — authenticated scenario controls and visible weights.
- `sih_assets/scenario_panel.png` — scenario panel after the live run.
- `sih_assets/simulation_result.png` — actual result state with allocation, class totals and affected unit ID.
- `sih_assets/decision_insight_offline_fallback.png` — actual AI unavailable fallback and limitations.
- `sih_assets/decision_insight.png` — focused decision insight panel.

## Architecture

- `sih_assets/system_architecture.svg` — clean slide-ready actual architecture.
- `sih_assets/system_architecture.md` — architecture notes and Mermaid diagram.
- `sih_assets/application_workflow.md` — user workflow.
- `sih_assets/ai_rag_pipeline.md` and `sih_assets/ai_rag_architecture.md` — AI/RAG path and limits.
- `sih_assets/scenario_simulation_pipeline.md` — deterministic simulation pipeline.
- `sih_assets/before_after_workflow.md` — workflow comparison.
- `sih_assets/data_flow.md` — implemented data flow.

## Metrics

See `sih_assets/project_metrics.json` and `sih_assets/project_metrics.md`.

Verified values include 6 implemented API routes, 3 migrations, 1 dataset, 1 version, 1 region, 3 land-use observations, 1 document, 3 indexed chunks, 4 roles, 11 passing foundation tests and `llm_available: false` during capture. Mutable local database counts should be rechecked immediately before submission.

## Demo Results

See `sih_assets/demo_results.md`.

The live run searched `agricultural conversion`, used the seeded UI defaults, allocated `9000 m²` to `unit-001`, and returned `15000 m²` agriculture plus `9000 m²` built-up in the scenario. The local AI fallback reported that llama.cpp was offline. All values are synthetic/demo values.

## References

- Project documentation: `Prd.md`, `Architecture.md`, `Design.md`, `Rules.md`, `Phases.md`, `Memory.md`, `Security and review.md`, `README.md`.
- Actual source modules listed above.
- No external government/public data reference is claimed because none is present in the seeded demo.

## Claims requiring verification

- Team ID and team name.
- Final SIH problem-statement metadata and submission template.
- Any official/public dataset, publisher, license, source URL, CRS and boundary claims added later.
- Whether the local llama.cpp server and GGUF model will be running during the final live presentation.
- Mutable local counts such as users, audit rows and persisted scenario runs.
- Do not describe the placeholder map as interactive GIS.
- Do not describe FTS5 as semantic or hybrid RAG.
- Do not describe the simulator as a forecast, causal model or authoritative prediction.
