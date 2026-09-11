# Verified Project Metrics

Verified on 2026-09-11 from the current workspace and local demo database.

| Metric | Value | Source |
|---|---:|---|
| Implemented API routes | 6 | `backend/app.py` |
| Numbered migrations | 3 | `core/database/migrations/` |
| Datasets | 1 | `database/ps26019.db`, `datasets` |
| Dataset versions | 1 | `dataset_versions` |
| Regions | 1 | `regions` |
| Land-use observations | 3 | `landuse_observations` |
| Documents | 1 | `documents` |
| Indexed document chunks | 3 | `document_chunks` |
| Roles | 4 | `roles` |
| Users | 5 at capture time | `users` |
| Persisted scenario runs | 6 at capture time | `scenario_runs` |
| Foundation tests | 11 passing | `tests/test_foundation.py` |
| Live local LLM available | false during capture | `GET /api/health` |

## Live analytics values

`GET /api/analytics` returned:

- 2020 agriculture: `10000.0 m²`.
- 2020 built-up: `8000.0 m²`.
- 2024 built-up: `10000.0 m²`.
- Agriculture change: `-10000.0 m²`.
- Built-up change: `2000.0 m²`.
- Observation count: `3`.

These are synthetic fixture values, not official measurements or performance claims. Database counts are mutable local demo-state values and should be rechecked immediately before submission.
