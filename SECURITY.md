# Security Policy

## Supported use

This project is an offline-first local MVP. It is not configured as a public internet service by default.

Before deployment:

- use a secret manager for administrator credentials and environment variables;
- set `APP_ENV=production` and explicit HTTPS `CORS_ORIGINS` values;
- keep databases, local models, raw documents and generated archives out of version control;
- run the API behind HTTPS, a reverse proxy, authentication controls, rate limiting and monitoring;
- remove or anonymize personal or confidential data from demo fixtures.

## Reporting a vulnerability

Do not publish credentials, tokens, private data or proof-of-concept payloads in a public issue. Report security concerns privately to the repository maintainers using the contact or private reporting channel configured in the GitHub repository.

Include the affected component, impact, reproduction steps and any proposed mitigation. Allow maintainers reasonable time to investigate before public disclosure.