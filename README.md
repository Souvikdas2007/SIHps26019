# PS26019

Offline-first evidence-to-decision platform for land governance.

## Current foundation

Phase 1 has established the SQLite schema, migration runner, environment configuration and replaceable profile contracts. Real datasets and the API are not implemented yet.

## Initialize the local database

```bash
python3 scripts/init_database.py
```

The default database is `database/ps26019.db`. Override it with `DATABASE_URL` using the `sqlite:///` scheme.

## Use the Makefile

From the repository root, run `make help` to list available commands. The usual first-time setup is:

```bash
make setup
make admin
make run
```

`make setup` creates or reuses `.venv`, installs backend and frontend dependencies,
initializes SQLite and seeds the synthetic demo. `make run` starts the backend,
frontend and llama.cpp together. `make run-all` remains an alias for `make run`.
Stop all PS26019 services with:

```bash
make kill
```

Override `PYTHON`, `NPM`, host/port variables, or
`LLAMA_SERVER`/`LLAMA_MODEL` when your environment uses different paths.

Run the full verification workflow with:

```bash
make check
```

## Run foundation tests

```bash
python3 -m unittest discover -s tests -v
```

## Seed the offline synthetic demo

```bash
python3 scripts/seed_demo.py
```

The seed is explicitly synthetic and is for local regression/demo use; it is
not official Kolkata or government data.

## Run the API

```bash
uvicorn backend.app:app --reload
```

The API provides `/api/health`, `/api/evidence`, `/api/analytics`,
`/api/catalog`, `/api/scenarios/run` and `/api/insights`. Authenticated admins
and researchers can register existing local GeoJSON datasets through the
catalog module; admins can register local model metadata.

Create a local admin before using protected insight/scenario actions:

```bash
export PS26019_ADMIN_USERNAME=admin
export PS26019_ADMIN_PASSWORD='use-a-password-at-least-12-chars'
python3 scripts/create_admin.py
```

Log in with those credentials in the frontend. Evidence search and analytics
remain available without login.

## Build the frontend

```bash
cd frontend
npm install
npm run build
```

The frontend expects the API at `http://127.0.0.1:8000`.

The **Catalog** workspace section lists registered dataset versions and local
models. Dataset registration accepts existing project-relative `.geojson` files
under `data/`; model registration accepts existing files under `models/` and
stores versioned metadata in SQLite. It does not upload files or expose local
filesystem paths outside those project directories.

## Security before deployment

- Never commit `.env`, database files, local models, raw documents or generated archives. The repository ignore rules exclude these by default; review `git status --ignored` before the first push.
- Keep `APP_ENV=local` for the demo. For production, set explicit HTTPS values in `CORS_ORIGINS`; the application rejects wildcard and HTTP origins in that mode.
- Set `PS26019_ADMIN_PASSWORD` only in the shell or a secret manager. Do not place credentials in `.env.example`, source files or issue reports.
- Serve the API behind HTTPS and a reverse proxy with authentication, request limits and access logs. The application adds baseline browser security headers but is not a complete internet-facing deployment boundary.
- Review [Security and review.md](Security%20and%20review.md) and [SECURITY.md](SECURITY.md) before publishing sensitive datasets.

## Install application dependencies

The runtime dependencies are declared in `requirements.txt` and are intentionally not required for the standard-library database tests.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

Large spatial assets, documents and local models belong under `data/` and `models/local/`; SQLite stores their metadata and references.
