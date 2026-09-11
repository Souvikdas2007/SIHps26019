# Security and Review — PS26019

## 1. Security Objectives

- protect accounts;
- protect SQLite database;
- preserve provenance;
- prevent unauthorized scenario changes;
- defend RAG against prompt injection;
- keep AI non-authoritative;
- maintain auditability.

## 2. Authentication/Authorization

Suggested roles:

```text
ADMIN
POLICY_ANALYST
RESEARCHER
VIEWER
```

Authorization is enforced server-side.

Never store plaintext passwords or expose tokens.

## 3. SQLite Security

- restrict database-file permissions;
- never serve the `.db` file publicly;
- use parameterized queries;
- enable foreign keys;
- use migrations;
- back up before destructive changes;
- protect backups;
- do not store sensitive database copies in Git.

## 4. API Security

Every endpoint:
- validates input;
- checks authorization;
- limits request size;
- returns safe errors;
- avoids stack traces;
- rate-limits expensive operations where appropriate.

## 5. Scenario Security

Validate:
- percentages;
- numeric ranges;
- region/layer/scenario IDs;
- model versions.

Never inject untrusted values into SQL, shell commands, paths or executable code.

## 6. Geospatial Uploads

If uploads are supported:
- allow-list file types;
- enforce size limits;
- inspect archives;
- validate CRS/geometry;
- prevent path traversal;
- never execute uploaded content.

## 7. Local AI/RAG Security

Threats:
- prompt injection;
- malicious retrieved text;
- hallucinated citations;
- data leakage;
- resource exhaustion;
- generated output being treated as commands.

Controls:
1. Retrieved text is data, not instructions.
2. Separate system instructions from retrieved content.
3. LLM cannot execute SQL/shell/application actions.
4. Validate structured output.
5. Do not expose shell tools to the model.
6. Apply token/time limits.
7. Validate citations against retrieved sources.
8. Sanitize rendered output.

## 8. Local LLM Runtime

Treat the local model server as a dependency, not an authority.

Use:
- configured local endpoint only;
- connection timeouts;
- model allow-list/configuration;
- graceful offline behavior.

Never put secrets into prompts.

## 9. Data Privacy

Minimize personal data.

Do not ingest individual landholder information merely to enrich the demo.

## 10. Provenance

Record:

```text
source
publisher
source URL
data year
acquisition date
version
spatial resolution
processing version
license/usage terms
```

Simulation results record model version, input data versions, parameters, weights, timestamp and scenario ID.

## 11. Audit

Record:
- authentication events;
- authorization failures;
- scenario creation/execution;
- data/model versions;
- administrative changes;
- significant errors;
- AI runtime status.

## 12. Simulation Review

Test:
- area calculations;
- baseline/scenario arithmetic;
- no double-counting;
- geometry selection;
- 0% scenario;
- maximum allowed scenario;
- empty/invalid region;
- deterministic repeated runs.

Do not claim causality, guaranteed outcomes or validated forecasts without evidence.

## 13. AI Review

Test:
- prompt injection;
- irrelevant/missing evidence;
- conflicting sources;
- unsupported questions;
- citation correctness;
- numerical consistency;
- local runtime unavailable.

Required fallback:

> **Insufficient evidence available in the current knowledge base.**

AI explains supplied simulation results; it does not replace them.

## 14. Pre-Demo Checklist

### Functional
- [ ] Evidence search works
- [ ] Sources visible
- [ ] Map works
- [ ] Historical comparison works
- [ ] Simulation works
- [ ] Baseline/scenario metrics agree
- [ ] Impact geometry is correct
- [ ] AI insight is grounded

### Local AI
- [ ] llama.cpp/runtime starts
- [ ] Chat model loaded
- [ ] Embedding model loaded
- [ ] Retrieval index ready
- [ ] AI failure fallback works
- [ ] No cloud AI dependency

### Security
- [x] No secrets in repository
- [x] Auth tested
- [x] Authorization tested
- [x] Inputs validated
- [ ] File uploads restricted
- [x] Prompt injection content treated as untrusted data
- [x] SQLite not publicly exposed

### Data/Model
- [ ] Sources documented
- [ ] CRS verified
- [ ] Geometry validity checked
- [ ] Versions recorded
- [ ] License reviewed
- [ ] Formula/weights documented
- [ ] Assumptions visible
- [ ] Results reproducible

## 15. Release Gate

Current status: PARTIALLY READY for a synthetic local demo. Do not treat this
as production-ready until the remaining review items below are complete:

- role-specific endpoint coverage beyond the current protected routes;
- rate limiting and request-size limits;
- upload security if uploads are enabled;
- structured AI output and citation validation;
- official dataset provenance and geometry review.

Do not release if:
- core calculations are unverified;
- sources cannot be traced;
- unauthorized modification is possible;
- AI produces unsupported citations;
- simulation is presented as guaranteed prediction;
- secrets are exposed;
- core functionality requires the local LLM.

The MVP is ready when it is **functional, reproducible, explainable, portable and secure enough for its intended demo scope**.
