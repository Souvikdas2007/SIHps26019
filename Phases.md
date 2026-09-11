# Phases — PS26019 MVP

## Phase 0 — Freeze

Lock:
- SQLite;
- local LLM/RAG;
- Evidence Explorer;
- GIS;
- analytics;
- one simulator;
- AI insight.

No microservices or cloud AI.

## Phase 1 — Data Foundation

Tasks:
1. SQLite schema + migrations.
2. Dataset/document metadata.
3. Raw/processed folders.
4. Load selected LULC and supporting layers.
5. Validate geometry/CRS.
6. Record provenance.

Status: PARTIALLY COMPLETED

Completed:
- SQLite migration runner with idempotent numbered migrations.
- Provenance-oriented schema for users, evidence, datasets, regions, observations, scenarios, models and audit logs.
- SQLite FTS5 document chunk index.
- Environment-driven local configuration.
- Replaceable profile contracts for datasets and unresolved project choices.
- Dependency-free GeoJSON catalog importer for prepared small assets.
- Synthetic Kolkata-like LULC fixture covering agriculture and built-up observations across two years.
- Dataset profile identifier and checksum persistence.
- Portable raw, processed, document and model directories.
- Foundation tests for foreign keys, migration idempotency, profile isolation and synthetic ingestion.

Remaining:
- Select and document the bounded Kolkata study area.
- Select and ingest the demonstration LULC/supporting datasets.
- Validate real geometry and CRS values.
- Register imported dataset versions and processing checksums.

Test-only validation complete:
- Synthetic GeoJSON ingestion registers dataset, version, region and observations.
- Missing observation properties are rejected.

Deliverable: portable SQLite database + processed data.

## Phase 2 — GIS + Analytics

Status: PARTIALLY COMPLETED

Completed:
- Deterministic land-use totals, percentages and period-over-period changes.
- Analytics API endpoint.
- Synthetic GeoJSON study-area asset for offline regression/demo use.
- Frontend observed KPI/map placeholder surface.

Remaining:
- Production GeoPandas/Shapely geometry validation and browser map layer rendering.

Tasks:
1. Map page.
2. Region selection.
3. LULC layers.
4. Historical comparison.
5. Land-use KPIs.
6. Change calculations.
7. Simplified GeoJSON.

Deliverable: working observed-data analysis.

## Phase 3 — Local RAG

Status: PARTIALLY COMPLETED

Completed:
- Local document/chunk indexing into SQLite FTS5.
- Source-attributed keyword retrieval and snippets.
- Evidence API endpoint.

Remaining:
- Document extraction pipeline for PDFs/HTML.
- Local embeddings and hybrid semantic ranking.

Tasks:
1. Curate trusted corpus.
2. Extract and chunk documents.
3. SQLite metadata + FTS5.
4. Local embeddings.
5. Hybrid retrieval.
6. llama.cpp provider adapter.
7. Citation/source display.
8. Grounded synthesis.

Deliverable: local evidence search and explanation.

## Phase 4 — Policy Simulator

Status: PARTIALLY COMPLETED

Completed:
- Deterministic factor scoring, eligibility filtering, stable ranking and partial allocation.
- Baseline/scenario metrics and affected unit identifiers.
- Scenario API endpoint and repeatability tests.

Remaining:
- Persist scenario requests and results through the API.
- Generate affected geometry from selected spatial assets.

Scenario:

> Agricultural-to-built-up conversion around an expanding urban area.

Tasks:
1. Eligibility.
2. Constraints.
3. Factors.
4. Normalization.
5. Weights.
6. Ranking.
7. Allocation.
8. Recalculation.
9. Scenario persistence.
10. Affected geometry.

Deliverable: deterministic what-if analysis.

## Phase 5 — Local AI Insight

Status: PARTIALLY COMPLETED

Completed:
- `LLMProvider` contract and llama.cpp HTTP adapter.
- Grounded prompt construction with source IDs and deterministic results.
- Explicit offline/unavailable fallback.

Remaining:
- Validate structured model output and citations against retrieved sources.
- Run with a prepared local GGUF model.

Tasks:
1. Retrieve evidence.
2. Collect simulation output.
3. Build structured context.
4. Call local LLM.
5. Generate summary/observations/assumptions/limitations/citations.
6. Validate output.

Deliverable: grounded local AI explanation.

## Phase 6 — Integration + Demo

Status: PARTIALLY COMPLETED

Completed:
- FastAPI modular-monolith application.
- React/Vite policy-intelligence workspace shell.
- Synthetic offline seed command.
- End-to-end API smoke validation.

Remaining:
- Connect a real interactive map library.
- Add richer loading/error states for every workflow action.
- Persisted scenario runs now exist; complete the three-minute demo flow with map impact rendering.

New frontend workflow:
- Login/logout and local session state.
- Requested conversion-area control.
- Four visible factor-weight controls.
- Deterministic simulation execution.
- Allocated area, class totals and affected-unit results.
- Recent local run summaries.

```text
Question → Evidence → Region → GIS → Analytics
→ Scenario → Simulation → Impact → Local AI Insight
```

Tasks:
- polish UI;
- loading/error states;
- local LLM health check;
- preload fallback data/model;
- rehearse 3-minute demo.

## Phase 7 — Security + Review

Status: PARTIALLY COMPLETED

Completed:
- Local scrypt password hashing with no plaintext password storage.
- SQLite-backed bearer sessions with expiry checks.
- Login endpoint and protected scenario/insight routes.
- Scenario, scenario-run and scenario-result persistence with result checksums.
- Audit events for login success/failure, scenario execution and insight requests.
- API integration validation for unauthorized and authorized scenario execution.

Remaining:
- Role-specific authorization rules beyond authenticated access.
- Rate limiting and request-size limits.
- Upload security, because uploads are not enabled yet.
- Structured AI output and citation validation.
- Full pre-demo security review and dependency audit.

Check:
- SQLite permissions;
- auth/authorization;
- input validation;
- file safety;
- prompt injection;
- citation correctness;
- simulation determinism;
- geometry correctness;
- provenance;
- secrets/dependencies.

## Suggested Short Timeline

| Phase | Effort |
|---|---:|
| Freeze | 0.5 day |
| Data | 1–2 days |
| GIS + Analytics | 2 days |
| Local RAG | 1–2 days |
| Simulator | 2 days |
| AI Insight | 1 day |
| Integration/Demo | 1–2 days |
| Review | 0.5–1 day |

If time is tight:

**Simulator + GIS + Evidence retrieval > UI polish > future features.**

## Phase 8 — SIH Presentation / PDF Preparation

Status: COMPLETED for the current synthetic local MVP evidence package.

Tasks:

- [x] Inspect the implemented frontend, backend, database, AI/RAG, GIS/data, simulation, auth and tests.
- [x] Reconcile planned documentation with actual code and record discrepancies.
- [x] Run the seeded live application workflow.
- [x] Capture real workspace, evidence, geography, analytics, scenario and insight screenshots.
- [x] Generate actual system architecture and data-flow diagrams.
- [x] Generate AI/RAG, workflow, simulation and before/after diagrams.
- [x] Collect verified database, API, test and live-result metrics.
- [x] Prepare six-slide SIH content mapping.
- [x] Prepare final SIH PDF package index.
- [x] Update `Memory.md` with the current submission-preparation state.
- [x] Document missing or partially implemented features instead of fabricating evidence.

Remaining submission work outside this phase:

- [ ] Verify team ID/name and final SIH template metadata.
- [ ] Recheck mutable local metrics immediately before submission.
- [ ] Add official/public data references only after provenance, CRS and license review.
- [ ] Decide whether the final live demo will run the local llama.cpp server.

## Phase 9 — Next-Generation Frontend & Dynamic Application UX

Status: IMPLEMENTED with known MVP limitations.

Objective:

- Replace the single long workspace with a professional routed application that makes the evidence-to-decision workflow legible.

Scope and implementation:

- Added real React routes for dashboard, evidence, geography, analytics, scenarios, insights, data/models and settings.
- Added a persistent application shell with active sidebar navigation, mobile drawer behavior, system status and logout.
- Added a centralized typed API service while preserving all existing REST contracts and bearer-token protection.
- Moved evidence search, analytics refresh, scenario execution, insight generation and catalog loading into dedicated views.
- Added explicit observed, simulated, AI-generated, synthetic and unavailable states.
- Added responsive policy-intelligence styling, workflow cues, data tables, map placeholder controls, comparison results, empty/error states and reduced-motion support.
- Added `react-router-dom` to the frontend dependencies.

Validation:

- `cd frontend && npm run build` passes.

Completed items:

- Routed navigation and root redirect.
- Dashboard with real analytics values when available.
- Evidence Explorer using `GET /api/evidence`.
- Analytics using `GET /api/analytics`.
- Protected scenario flow using `POST /api/scenarios/run`.
- Protected insight flow using `POST /api/insights`.
- Protected Data & Models view using `GET /api/catalog`.
- Login/logout using the existing `POST /api/auth/login` bearer workflow.
- Explicit map limitation disclosure.

Remaining items:

- Real browser GIS geometry rendering and affected-unit visualization.
- Persisted scenario-history retrieval endpoint.
- Full Playwright viewport and console regression pass against live services.

Next phase:

- Connect the prepared GeoJSON asset to a lightweight browser map without changing simulation mathematics, then validate the full workflow at 375, 480, 768, 1024, 1440 and 1920 pixels.
