# Implementation Status

## IMPLEMENTED

- React/Vite single-page policy-intelligence workspace.
- Workspace, Evidence, Geography, Scenarios and Decision Insight sections.
- Local login with bearer session token stored in browser local storage.
- FastAPI routes for health, login, evidence, analytics, scenario execution and insight requests.
- SQLite migrations, foreign keys, metadata schema and audit tables.
- SQLite FTS5 lexical retrieval with source IDs, titles and snippets.
- Synthetic GeoJSON import with required-property validation, dataset/version/region registration and checksum.
- Deterministic land-use totals, percentages and first-to-last period changes.
- Deterministic agricultural-to-built-up scoring, ranking, partial allocation and baseline/scenario output.
- Scenario/result persistence and SHA-256 result checksum.
- Scrypt password hashing, expiring sessions and ADMIN/POLICY_ANALYST/RESEARCHER/VIEWER roles.
- Grounded prompt construction and llama.cpp HTTP adapter.
- Explicit AI unavailable fallback preserving supplied deterministic scenario results.
- Responsive frontend controls, layer toggles, error/toast states and production build.

## PARTIALLY IMPLEMENTED

- GIS: GeoJSON ingestion and a frontend geography panel exist, but the browser map is a styled placeholder. No MapLibre/Leaflet rendering or geometry display exists.
- RAG: FTS5 lexical retrieval exists; embeddings, vector search and hybrid ranking do not.
- AI explanation: local llama.cpp path exists and fallback is verified; the model server was offline during this asset capture, so no generated explanation is claimed here.
- Data provenance: synthetic profile/version/checksum metadata exists; official source, license, boundary and production geometry review remain.
- Scenario persistence: API persists runs; the frontend recent-runs list is session-local only.

## NOT IMPLEMENTED

- Official government/public dataset integration.
- Real interactive GIS map, feature inspection or affected-area geometry rendering.
- CRS transformation, geometry repair, spatial joins, buffers, intersections or proximity processing in the application path.
- PDF/HTML document extraction pipeline.
- Local embeddings, vector index, semantic/hybrid retrieval.
- Structured AI output validation and citation verification.
- Rate limiting, request-size limits and full dependency audit.
- Logout/revocation endpoint, user administration API and broader role-specific endpoint coverage.

## Verification basis

The status above is grounded in the current source tree, database seed, live browser run, live API responses, frontend build, Python compilation and 11 passing foundation tests. Planned capabilities in `Prd.md`, `Architecture.md` and `Design.md` are not treated as implemented unless present in code.
