# Getting started

This guide focuses on **testing the full app with Docker**. You can run the API, minimal UI, audit, and either OpenAI, Anthropic, or Ollama (or a combination) in a few steps. A shorter path for **tests only** and **running the app on the host** is at the end.

---

## Prerequisites

| Requirement | Purpose |
|-------------|---------|
| **Docker** and **Docker Compose** | Run Postgres, the app, and optionally Ollama in containers. [Install Docker](https://docs.docker.com/get-docker/). |
| **Python 3.11+** (on your host) | Run database migrations and the test suite. Not required for running the app in Docker. |
| **Public LLM API key** (optional) | Use a cloud provider (OpenAI or Anthropic) as default. Set `PUBLIC_LLM_API_KEY`; get keys at [platform.openai.com](https://platform.openai.com/api-keys) or [console.anthropic.com](https://console.anthropic.com). |
| **Ollama** (optional) | Use a local model as default or fallback. Run via Docker in this guide; no separate install. |

You need **at least one** of: public LLM (set `PUBLIC_LLM_API_KEY` for OpenAI or Anthropic) or local LLM (Ollama with a model pulled). The app will not respond to chat until one provider is configured.

---

## Part 1: Test the full app with Docker

Follow these steps in order. All commands are run from the **repository root** unless noted.

---

### Step 1. Clone and prepare the repo

```bash
git clone https://github.com/LiorAbitbol/policy-mesh.git
cd policy-mesh
```

If you want to run tests or migrations locally, create a virtualenv and install:

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

### Step 2. Create and edit `.env`

Create your environment file from the example:

```bash
cp .env.example .env
```

Edit `.env` in a text editor. You **must** set at least the following for the full app with audit and a working chat provider.

#### Required: policy file (POLICY_FILE)

Policy (sensitivity keywords, cost thresholds, default provider) is loaded from a JSON file only. **POLICY_FILE** must be set to the path of that file. If unset, or if the file is missing or invalid JSON, the application errors.

**Where the policy file lives:**
- **Default:** The repo includes **`app/policies.example.json`**. Set **`POLICY_FILE=./app/policies.example.json`** in `.env` for both host and Docker; the image uses this by default. No copy needed to run.
- **Local override:** To customize, create **`app/policies.json`** (gitignored) and set `POLICY_FILE=./app/policies.json`, or copy: `cp app/policies.example.json app/policies.json` and edit. See [Policy file schema](policy_file_schema.md).

#### Required for audit (Postgres)

The default values in `.env.example` match the Postgres container. If you didn’t change them, you can leave these as-is:

- `POSTGRES_USER=policy_mesh`
- `POSTGRES_PASSWORD=change-me`
- `POSTGRES_DB=policy_mesh`
- `DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@localhost:5432/policy_mesh`

**Important:** Keep `DATABASE_URL` with **host `localhost`** in `.env`. The app container gets a different URL (host `postgres`) from `docker-compose.yml` automatically. You use `localhost` only when running migrations from your machine (Step 4).

#### Required for chat: choose a default provider

Set the default in your **policy file** (`cost.default_provider`): **`local`** or **`public`** only. When `public`, which concrete provider (OpenAI vs Anthropic) is determined by **PUBLIC_LLM_URL** at runtime.

**Option A — Use a public LLM (OpenAI or Anthropic) as default**

- Set your public LLM API key in `.env`: `PUBLIC_LLM_API_KEY=sk-your-actual-key-here`, and set **PUBLIC_LLM_URL** if needed (defaults to OpenAI; use an Anthropic URL for Anthropic).
- In `policies.json`, set `"cost": { ..., "default_provider": "public" }`.

**Option B — Use Ollama (local) as default**

- In `policies.json`, set `"cost": { ..., "default_provider": "local" }`.
- Do **not** set `PUBLIC_LLM_API_KEY` unless you also want to allow cloud fallback.
- In Step 5 you will start Ollama and pull a model.

**Optional:** See `.env.example` for providers and timeouts; routing policy is in the policy file only.

Save and close `.env`.

---

### Step 3. Start Postgres

Start only the Postgres service and wait until it is healthy:

```bash
docker compose up -d postgres
docker compose ps
```

In the table, the `postgres` service should show `healthy` in the STATUS column. If it says `starting`, wait a few seconds and run `docker compose ps` again.

---

### Step 4. Run database migrations (from your host)

Migrations run on your machine and connect to Postgres via `localhost` (port 5432 is exposed by the container). Use the **same** user, password, and database name as in your `.env` (e.g. `policy_mesh` / `change-me` / `policy_mesh`).

**If you use the default credentials from `.env.example`:**

```bash
export DATABASE_URL=postgresql+psycopg://policy_mesh:change-me@localhost:5432/policy_mesh
alembic upgrade head
```

**If you changed Postgres credentials in `.env`**, set `DATABASE_URL` to match (with host `localhost`):

```bash
export DATABASE_URL=postgresql+psycopg://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DB
alembic upgrade head
```

You should see output like `INFO  [alembic.runtime.migration] Running upgrade ... -> ..., head`. Then:

```bash
alembic current
```

This prints the current revision (e.g. `head`). You only need to run migrations once per new database (or after pulling changes that add migrations).

---

### Step 5. Start the app (and optionally Ollama)

Start the app container. It will load `.env` and use the overridden `DATABASE_URL` (host `postgres`) from `docker-compose.yml`:

```bash
docker compose up -d app
docker compose ps
```

Wait until the `app` service shows `healthy`. The first time, `docker compose up -d app` may build the image; that can take a minute.

**If you chose Ollama as default (Option B in Step 2):**

Start Ollama and pull a model so the app can call it:

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull llama2
```

After the pull finishes, the app can route chat to local. You can leave Ollama stopped if you use only OpenAI or Anthropic.

---

### Step 6. Verify the app

Run these in order. Use a second terminal if the first is busy.

**6a. Health**

```bash
curl -s http://127.0.0.1:8000/v1/health
```

Expected: `{"status":"ok"}` (or similar JSON with `status`).

**6b. Routing rules (policy)**

```bash
curl -s http://127.0.0.1:8000/v1/routes
```

Expected: JSON with `rule_order`, `default_provider`, `sensitivity_keyword_count`, cost fields, etc. This confirms the app is up and config is loaded.

**6c. Chat**

```bash
curl -s -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

Expected: JSON with `provider`, `reason_codes`, `content` (or `error`), and `request_id`. If you see `request_id`, audit is enabled and you can fetch that event (6d). **Note:** The app does not stream; it waits for the full LLM response, so chat can take 10–60 seconds depending on provider and model.

**6d. Audit (use a real `request_id` from the chat response)**

```bash
curl -s http://127.0.0.1:8000/v1/audit/REPLACE_WITH_REQUEST_ID
```

Replace `REPLACE_WITH_REQUEST_ID` with the `request_id` from the previous response. Expected: JSON with `request_id`, `decision`, `status`, `latency_ms`, etc. If audit is disabled or the ID is missing, you may get 404.

**6e. Minimal UI in the browser**

Open in your browser:

- **http://localhost:8000/**
  or
- **http://localhost:8000/ui**

You should see the Policy Mesh page with:

- **Chat** — Type a message and click **Send**. Responses are not streamed; the app waits for the full reply (often 10–60 seconds). The response (provider, reason_codes, content) appears below; the audit section updates with the last request’s audit event.
- **Routing rules** — Click **Load rules** to show the current policy (from `/v1/routes`).
- **Audit** — After a chat, the audit section shows the event for that request (from `/v1/audit/{request_id}`).

**6f. OpenAPI docs (optional)**

Open **http://localhost:8000/docs** to try the API interactively.

---

### Step 7. Stop everything

To stop all services:

```bash
docker compose down
```

To stop and **remove volumes** (deletes Postgres data and Ollama models):

```bash
docker compose down -v
```

---

## Part 2: Run tests only (no Docker required)

From the repo root with a virtualenv activated and deps installed (`pip install -e ".[dev]"`):

```bash
pytest tests/ -v
```

All tests use mocks (no real Postgres, Ollama, OpenAI, or Anthropic). You should see all tests pass.

---

## Part 3: Run the app on the host (no Docker)

If you prefer to run the app process on your machine instead of in Docker:

1. Start Postgres (e.g. `docker compose up -d postgres` or a local install).
2. In `.env`, set `DATABASE_URL` with host `localhost` (and correct user/password/db).
3. Run migrations: `export DATABASE_URL=... && alembic upgrade head`.
4. Start the app: `uvicorn app.main:app --reload` (with `DATABASE_URL` and provider vars in the environment, e.g. `set -a && source .env && set +a` or export them manually).
5. For Ollama, use `LOCAL_LLM_URL=http://localhost:11434` if Ollama runs on the host; for Docker Ollama, use `http://localhost:11434` from the host as well.

Then use the same verification steps (health, routes, chat, audit, UI at http://127.0.0.1:8000/).

---

## Quick reference

| Goal | Main steps |
|------|------------|
| **Full app in Docker (public LLM + audit)** | `.env` with `POLICY_FILE`, `PUBLIC_LLM_API_KEY` (OpenAI or Anthropic). Policy file: `cost.default_provider: "public"`. Postgres → migrations (localhost) → `docker compose up -d app` → verify. |
| **Full app in Docker (Ollama + audit)** | `.env` with `POLICY_FILE`. Policy file: `cost.default_provider: "local"`. Postgres → migrations → `docker compose up -d app` and `docker compose up -d ollama` + `ollama pull llama2` → verify. |
| **Tests only** | `pip install -e ".[dev]"` then `pytest tests/ -v`. |
| **App on host** | Postgres + migrations + `DATABASE_URL`, `POLICY_FILE`, and provider vars in env → `uvicorn app.main:app --reload`. |

---

## Troubleshooting

| Problem | What to do |
|--------|------------|
| **`/v1/chat` returns 500 or "Internal Server Error"** | Check app logs: `docker compose logs app`. Typical causes: (1) **Database** — Postgres not running or app can’t reach it. Ensure you ran Step 3 and 4; the app uses host `postgres` automatically. (2) **Public LLM** — Missing or invalid `PUBLIC_LLM_API_KEY` when default is **public** (and PUBLIC_LLM_URL points to OpenAI or Anthropic). (3) **Ollama** — If using local, start Ollama and pull a model; use `LOCAL_LLM_URL=http://ollama:11434` in Docker (already set in `docker-compose.yml`). |
| **"connection to server at 127.0.0.1 port 5432 failed"** | The app container is trying to use `localhost` for Postgres. Ensure `docker-compose.yml` has the `DATABASE_URL` override for the app service (host `postgres`). Your `.env` should keep `localhost` for migrations only. |
| **Audit not found (404)** | Audit is enabled only when `DATABASE_URL` is set and migrations have been run. Confirm `alembic upgrade head` succeeded and the app container has the overridden `DATABASE_URL` (with host `postgres`). |
| **"env file .env not found"** | Run `cp .env.example .env` in the repo root. If you use a different path, adjust `env_file` under the `app` service in `docker-compose.yml`. |
| **Tests fail with `ModuleNotFoundError`** | Activate the virtualenv and install deps: `pip install -e ".[dev]"` from the repo root. |
| **UI shows "error: ... is not valid JSON"** | The server returned a non-JSON error (e.g. 500 HTML). Check `docker compose logs app` for the real error and fix the cause (DB, provider config, etc.). |
