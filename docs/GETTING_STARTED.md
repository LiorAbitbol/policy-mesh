# Getting started

Follow these steps to clone the repo, run the test suite, and optionally run the app (with Docker, Postgres, and providers).

---

## Prerequisites

| Requirement | Used for | Notes |
|-------------|----------|--------|
| **Git** | Cloning the repo | Any recent version |
| **Python 3.11+** | Running the app and tests | Required for all paths |
| **Docker & Docker Compose** | Running Postgres, Ollama, and/or the app in containers | Optional if you only run tests or run the app on the host |
| **OpenAI API key** | Routing requests to the OpenAI provider | Optional; only needed if you want to test the cloud path (or set `DEFAULT_PROVIDER=openai`) |
| **Ollama** (optional) | Local LLM provider | Can run via Docker (`docker compose up -d ollama`) or [install locally](https://ollama.ai) |

You can run the full test suite with **only Python** (no Docker, no API keys). To run the app and hit `/v1/chat` with a real model, you need either Ollama (local) or an OpenAI key (cloud), or both.

---

## 1. Clone and install (everyone)

```bash
git clone https://github.com/LiorAbitbol/policy-mesh.git
cd policy-mesh
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 2. Run the test suite (no Docker, no keys)

From the repo root with the venv activated:

```bash
pytest tests/ -v
```

All tests use mocks (no real Postgres, Ollama, or OpenAI). You should see all tests pass (e.g. 34 tests).

---

## 3. Run the app (minimal: health only)

With the venv activated:

```bash
uvicorn app.main:app --reload
```

In another terminal:

```bash
curl http://127.0.0.1:8000/v1/health
# Expected: {"status":"ok"}
```

Open **http://127.0.0.1:8000/docs** for the OpenAPI UI. Without Postgres or provider config, `/v1/chat` will fail if called (audit or provider not configured); health and docs work.

---

## 4. Run the app with Postgres (audit enabled)

**4a. Start Postgres (Docker)**

```bash
cp .env.example .env
# Edit .env if you want different Postgres credentials
docker compose up -d postgres
docker compose ps   # Wait until postgres is healthy
```

**4b. Run migrations (from host)**

```bash
export DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@localhost:5432/policy_mesh
# Or: set -a && source .env && set +a
alembic upgrade head
alembic current
```

**4c. Start the app**

```bash
export DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@localhost:5432/policy_mesh
uvicorn app.main:app --reload
```

Now audit events will be written to Postgres for each `/v1/chat` request. You still need a provider (Ollama or OpenAI) to get a successful chat response.

---

## 5. Run the full stack with Docker (Postgres + Ollama + app)

This path runs Postgres, Ollama, and the app in containers. The app needs env vars (e.g. `DATABASE_URL`, optional `OPENAI_API_KEY`) from your machine; the default `docker-compose.yml` does not load `.env` (so CI can run without it). For local runs, add `env_file: .env` under the `app` service in `docker-compose.yml`, or pass variables via `environment:`.

**5a. Prepare env**

```bash
cp .env.example .env
```

Edit `.env` and set at least:

- **For audit:**
  `DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@postgres:5432/policy_mesh`
  (Use host `postgres` when the app runs in Docker.)

- **Optional – OpenAI:**
  `OPENAI_API_KEY=sk-your-key`
  (Only needed if you want requests to go to OpenAI; otherwise use local routing with Ollama.)

**5b. Add env to the app container (local run)**

Edit `docker-compose.yml` and under the `app` service add:

```yaml
env_file:
  - .env
```

(Or add only the variables you need under `environment:`.)

**5c. Start Postgres and run migrations (from host)**

```bash
docker compose up -d postgres
docker compose ps   # Wait until postgres is healthy
export DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@localhost:5432/policy_mesh
alembic upgrade head
```

**5d. Start Ollama and pull a model**

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull llama2
```

**5e. Start the app**

```bash
docker compose up -d app
docker compose ps   # Wait until app is healthy
```

**5f. Test**

```bash
curl http://127.0.0.1:8000/v1/health
curl -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

To force local (Ollama) routing, set `DEFAULT_PROVIDER=local` in `.env` (and ensure the app service loads it). Open **http://127.0.0.1:8000/docs** to use the interactive API UI.

The `/v1/chat` response includes a `request_id` field (and `X-Request-Id` header). When audit is enabled (DATABASE_URL set + migrations applied), you can fetch the corresponding safe audit event view (no raw prompt) via:

```bash
curl http://127.0.0.1:8000/v1/audit/<request_id>
```

---

## Quick reference

| Goal | Prerequisites | Command(s) |
|------|----------------|------------|
| Run tests only | Python 3.11+, venv | `pip install -e ".[dev]"` then `pytest tests/ -v` |
| Health + OpenAPI docs | Python, venv | `uvicorn app.main:app --reload` then open http://127.0.0.1:8000/docs |
| App + audit | Python, Docker, Postgres | Migrations + `DATABASE_URL` + `uvicorn` (or app in Docker with `env_file: .env`) |
| App + local LLM | Above + Ollama (Docker or host) | `docker compose up -d ollama` + pull model; set `DEFAULT_PROVIDER=local` to prefer local |
| App + OpenAI | Above + `OPENAI_API_KEY` in env | Set key in `.env` and ensure app container loads it when using Docker |

---

## Troubleshooting

- **Tests fail with `ModuleNotFoundError`**
  Ensure the venv is activated and you ran `pip install -e ".[dev]"` from the repo root.

- **App fails on startup with "No module named 'app.audit.repository'"**
  The app imports the audit layer at startup. If you run without `DATABASE_URL`, audit is disabled but the module must still load; ensure `sqlalchemy` and `psycopg[binary]` are installed (they are in the default deps).

- **`/v1/chat` returns 500 or "connection refused"**
  The chosen provider (Ollama or OpenAI) must be reachable and configured. For Ollama in Docker, use `OLLAMA_BASE_URL=http://ollama:11434` in the app container. For OpenAI, set `OPENAI_API_KEY`.

- **Audit not writing rows**
  Set `DATABASE_URL` and run migrations. If the app runs in Docker, use host `postgres` in `DATABASE_URL` and ensure the app service has that variable (e.g. via `env_file: .env`).

- **Docker Compose fails with "env file .env not found"**
  The default `docker-compose.yml` does not require `.env`. If you added `env_file: .env`, create the file with `cp .env.example .env`.
