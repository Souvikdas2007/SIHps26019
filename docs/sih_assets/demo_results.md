# Verified Demo Results

## Scope

This is the actual local browser/API run captured on 2026-09-11. The data is synthetic and explicitly not official Kolkata or government data.

## Input

- Policy question used for evidence search: `agricultural conversion`.
- Selected UI region: `Kolkata / peri-urban West Bengal`.
- Requested conversion area: `9000 m²`.
- Target class: `built_up` (frontend/API default).
- Scenario version: API default `demo-v1`.

## Assumptions

- `Synthetic offline demonstration data`.
- `Scores are decision-support heuristics`.
- Only candidates marked eligible and with `land_use_class = agriculture` are considered.
- The simulator is scenario analysis, not an authoritative prediction of future land use.

## Parameters

| Factor | Weight |
|---|---:|
| Urban proximity | 0.4 |
| Population pressure | 0.2 |
| Infrastructure access | 0.3 |
| Environmental constraint | 0.1 |

Candidates sent by the frontend:

| Unit | Area | Urban | Population | Infrastructure | Environment |
|---|---:|---:|---:|---:|---:|
| unit-001 | 10000 m² | 0.9 | 0.7 | 0.8 | 0.1 |
| unit-002 | 8000 m² | 0.6 | 0.8 | 0.7 | 0.4 |
| unit-003 | 6000 m² | 0.8 | 0.4 | 0.5 | 0.9 |

## Calculation

The implemented formula is:

`score = w_urban * urban_proximity + w_population * population_pressure + w_infrastructure * infrastructure_access - w_environment * environmental_constraint`

Scores returned by the deterministic simulator:

- `unit-001`: `0.73`
- `unit-002`: `0.57`
- `unit-003`: `0.46`

The stable descending rank selects `unit-001` first. The requested `9000 m²` is a partial allocation from its `10000 m²` area.

## Result

- Allocated area: `9000 m²`.
- Selected/affected unit identifier: `unit-001`.
- Scenario agriculture: `15000 m²`.
- Scenario built-up: `9000 m²`.
- Frontend result status: `Result ready`.
- Scenario persistence: API saved the scenario, run, result and audit event.

## Evidence used

The evidence query returned one source-attributed result:

- Source ID: `synthetic-policy-001`.
- Title: `Synthetic Urban Land Policy Note`.
- Snippet: `Controlled agricultural conversion should preserve environmental constraints.`

## AI result

The browser requested an insight after the scenario. The live health endpoint reported `llm_available: false`, so the actual UI returned:

> AI insight unavailable because the local LLM runtime is offline.

The UI also displayed the limitations that the simulation is not an authoritative prediction and numerical values are supplied by deterministic application code. No generated AI explanation is claimed in this package.

## Limitations

- Synthetic data and synthetic policy text only.
- The selected UI region currently does not alter the API request; API provenance selects the first available region/dataset.
- No real map or affected geometry is rendered.
- Scenario candidates are request-supplied values, not derived from stored geometry.
- Retrieval is lexical FTS5 only.
- AI structured output and citation validation are not implemented.
