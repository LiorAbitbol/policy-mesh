# Policy Mesh

Local-first AI gateway for controlled, auditable model routing.

## Purpose
Policy Mesh routes chat requests deterministically between local and cloud providers while enforcing cost/risk policy, recording audit events, and exposing baseline metrics.

## V1 Goals
- Deterministic routing between `ollama` (local) and `openai` (cloud).
- Explicit reason codes for every routing decision.
- Audit event persistence for every chat request.
- Prometheus-compatible metrics and structured logs.
- Simple CLI and simple UI.

## Data Persistence (V1)
- Audit event persistence targets Postgres.

## Current Status
This repository currently contains governance/docs scaffolding and task definitions. Application code is implemented incrementally through task-based workflow.

## Local Run/Test (T-101)
- Create venv: `python3 -m venv .venv`
- Activate venv: `source .venv/bin/activate`
- Install deps: `python -m pip install --upgrade pip && pip install -e ".[dev]"`
- Run app: `uvicorn app.main:app --reload`
- Health check: `curl http://127.0.0.1:8000/v1/health` -> `{"status":"ok"}`
- Run health test: `pytest tests/integration/test_health.py -v`

## Container Run (T-110)
- Build image: `docker build -t policy-mesh-app .`
- Run with compose: `docker compose up -d app`
- Health check: `curl http://127.0.0.1:8000/v1/health` -> `{"status":"ok"}`
- Compose health status: `docker compose ps` (app service shows `healthy` when ready)

## Local Postgres + Migrations (T-109)
- Copy env: `cp .env.example .env` (edit `.env` if needed)
- Start Postgres: `docker compose up -d postgres`
- Check health: `docker compose ps` (postgres shows `healthy` when ready)
- Export `DATABASE_URL` (Alembic does not auto-load `.env`):
  - `export DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@localhost:5432/policy_mesh`
  - Or load from `.env`: `set -a && source .env && set +a`
- Run migrations: `alembic upgrade head`
- Verify revision: `alembic current`

## Documentation Map
- `docs/STRUCTURE.md` - Annotated project tree and placement conventions.
- `docs/ARCHITECTURE.md` - V1 architecture, request lifecycle, boundaries.
- `docs/DECISIONS.md` - Decision log and dependency decision template.

## Context and Workflow
- `context/` contains public execution context (`PROJECT`, `SCOPE`, `TASKS`) and pointers.
- `context/private/` contains canonical internal playbooks and task records.
- AI-assisted development is used; detailed operational workflows are intentionally maintained in private docs.

## CI
- GitHub Actions workflow: `.github/workflows/ci.yml`
- Runs on pull requests and pushes to `main`.
- When Python sources exist under `app/` or `tests/`, the **python-tests** job installs dependencies (`pip install -e ".[dev]"`) and runs the full test suite (`pytest tests/ -v`). No Postgres or external services; audit integration tests use mocks.
- Also includes repo sanity checks and container smoke validation (build app image, run compose app, assert `/v1/health`).

## Repository Layout (Top Level)
- `.github/` - CI workflows.
- `context/` - Public project context and pointers.
- `docs/` - Architecture, structure, and decisions.
- `README.md` - This file.

## Next Steps
- Implement tasks in `context/TASKS.md` in order.
- Keep one task per PR-sized change.
- Update tests and docs with any interface or behavior changes.
