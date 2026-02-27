# Policy Mesh

Local-first AI gateway for controlled, auditable model routing.

## Purpose
Policy Mesh routes chat requests deterministically between local and cloud providers while enforcing cost/risk policy, recording audit events, and exposing baseline metrics.

## V1 Goals
- Deterministic routing between `ollama` (local) and `openai` (cloud).
- Explicit reason codes for every routing decision.
- Audit event persistence in Postgres for every chat request.
- Prometheus-compatible metrics and structured logs.
- HTTP API with OpenAPI interactive docs (`/docs`); CLI and simple UI not in M1.

## Data Persistence (V1)
- Audit events are persisted in Postgres (one row per request; prompt hash and metadata only, no raw prompts).

## Current Status
M1 (runnable vertical slice) is complete: `/v1/chat` → decision → provider → audit → metrics, with integration tests. Governance and task workflow live in `.context/`; application code is extended via task-based workflow.

## Interfaces (V1 / M1)
Implemented endpoints: `/v1/health`, `/v1/chat`, `/v1/metrics`. Use the **HTTP API** (e.g. `curl` or any client) or the **OpenAPI interactive docs** at `/docs` when the app is running. No CLI or custom UI in this release.

## Getting started

**Prerequisites:** Git, **Python 3.11+** (required). Optional: **Docker & Docker Compose** (for Postgres/Ollama/app), **OpenAI API key** (for cloud provider), **Ollama** (for local LLM).

1. **Clone and install:**
   `git clone https://github.com/LiorAbitbol/policy-mesh.git && cd policy-mesh`
   `python3 -m venv .venv && source .venv/bin/activate`
   `pip install -e ".[dev]"`

2. **Run tests (no Docker or keys):**
   `pytest tests/ -v`

3. **Run the app:**
   `uvicorn app.main:app --reload` → then open http://127.0.0.1:8000/docs

For full step-by-step instructions (Postgres, Ollama, Docker, env vars), see **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**.

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
- **Local override:** The committed `docker-compose.yml` does not load `.env` into the app container (so CI can run without a `.env` file). For local runs with `DATABASE_URL`, `OPENAI_API_KEY`, etc., add under the `app` service: `env_file: .env`. See `.context/private/TEST_DOCKER.md` for full Docker test steps.

## Local Postgres + Migrations (T-109)
- Copy env: `cp .env.example .env` (edit `.env` if needed)
- Start Postgres: `docker compose up -d postgres`
- Check health: `docker compose ps` (postgres shows `healthy` when ready)
- Export `DATABASE_URL` (Alembic does not auto-load `.env`):
  - `export DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@localhost:5432/policy_mesh`
  - Or load from `.env`: `set -a && source .env && set +a`
- Run migrations: `alembic upgrade head`
- Verify revision: `alembic current`

## Routing / Decision engine (T-102)
- Order: **sensitivity** (keyword in prompt → local) → **cost** (prompt length under threshold → local) → **default** (openai).
- Config via env: `SENSITIVITY_KEYWORDS` (comma-separated), `COST_MAX_PROMPT_LENGTH_FOR_LOCAL` (int), `DEFAULT_PROVIDER` (`openai` or `local`). Defaults: empty keywords, 1000, openai.
- Unit tests: `pytest tests/unit/test_decision_engine.py tests/unit/test_reason_codes.py -v`

## Providers (T-103)
- **Ollama**: Local provider. Run in container (`docker compose up -d ollama`) or on host; default URL `http://localhost:11434`. In compose, app gets `OLLAMA_BASE_URL=http://ollama:11434` to call containerized Ollama. Pull a model after Ollama is up: `docker compose exec ollama ollama pull llama2` (or use host Ollama).
- **OpenAI**: Set `OPENAI_API_KEY` in env (no default; no secrets in code). Optional `OPENAI_BASE_URL` for proxy.
- **Timeouts**: `PROVIDER_TIMEOUT_SECONDS` (default 60).
- **Full demo with compose**: `docker compose up -d postgres ollama app` then call `/v1/chat` (or use scripts). Ensure `.env` has `DATABASE_URL` and optionally `OPENAI_API_KEY` for OpenAI routing.
- Provider integration tests (mocked HTTP): `pytest tests/integration/test_providers.py -v`

## POST /v1/chat (T-105)
- **Request**: `POST /v1/chat` with JSON body `{ "messages": [ { "role": "user", "content": "..." } ], "model": null }`. `messages` is required (at least one); `model` is optional (provider default if omitted).
- **Response**: `{ "provider": "local"|"openai", "reason_codes": ["..."], "content": "..." }` on success, or `"content": null, "error": "..."` on provider failure. Always includes `provider` and `reason_codes`.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"Hello"}]}'
  ```
- Flow: decision → provider call → audit write → metrics → response. Integration tests: `pytest tests/integration/test_chat_flow.py -v`

## GET /v1/metrics (T-106)
- **Prometheus exposition**: `GET /v1/metrics` returns `chat_requests_total` (labels: provider, status) and `chat_request_latency_seconds` (label: provider). Content-Type: `text/plain; version=0.0.4; charset=utf-8`. Scrape with Prometheus or `curl http://127.0.0.1:8000/v1/metrics`. Integration tests: `pytest tests/integration/test_metrics.py -v`

## Documentation Map
- **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Prerequisites and step-by-step: clone, run tests, run app (local or Docker).
- `docs/STRUCTURE.md` - Annotated project tree and placement conventions.
- `docs/ARCHITECTURE.md` - V1 architecture, request lifecycle, boundaries.
- `docs/DECISIONS.md` - Decision log and dependency decision template.
- `.context/` - Execution context: `PROJECT.md`, `SCOPE.md`, `TASKS.md`, `RULES.md`, `AGENTS.md` (see `.context/README.md`).

## Context and Workflow
- `.context/` contains public execution context (`PROJECT`, `SCOPE`, `TASKS`) and pointers.
- `.context/private/` contains canonical internal playbooks and task records.
- AI-assisted development is used; detailed operational workflows are intentionally maintained in private docs.

## CI
- GitHub Actions workflow: `.github/workflows/ci.yml`
- Runs on pull requests and pushes to `main`.
- When Python sources exist under `app/` or `tests/`, the **python-tests** job installs dependencies (`pip install -e ".[dev]"`) and runs the full test suite (`pytest tests/ -v`). No Postgres or external services; audit integration tests use mocks.
- Also includes repo sanity checks and container smoke validation (build app image, run compose app, assert `/v1/health`).

## Repository Layout (Top Level)
- `.github/` - CI workflows.
- `.context/` - Public project context and pointers.
- `docs/` - Architecture, structure, and decisions.
- `README.md` - This file.

## Next Steps
- Implement tasks in `.context/TASKS.md` in order.
- Keep one task per PR-sized change.
- Update tests and docs with any interface or behavior changes.
