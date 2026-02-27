# Policy Mesh

A local-first AI gateway that routes chat requests between local and cloud providers based on configurable policy, with audit, metrics, and a minimal UI.

## Tech stack

**Python 3.11+**, **FastAPI**, **PostgreSQL**, **Ollama** (local LLM), **OpenAI** (cloud). Run with **Docker Compose** or on the host. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full stack and request flow.

## What it does

- **Routes** each request deterministically: sensitivity (keywords) → cost (length or USD threshold) → default provider.
- **Supports** Ollama (local) and OpenAI (cloud). Every decision returns explicit reason codes.
- **Persists** one audit event per chat (prompt hash and metadata only; no raw prompts).
- **Exposes** Prometheus-compatible metrics and a read-only view of the effective routing policy (`/v1/routes`).
- **Serves** a minimal static UI at `/` and `/ui` for chat, rules, and audit.

## Quick start

```bash
git clone https://github.com/LiorAbitbol/policy-mesh.git && cd policy-mesh
cp .env.example .env   # edit with your API key and/or provider choices
```

**Run with Docker (recommended):** Postgres → migrations → app (and optionally Ollama). Full step-by-step: **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**.

**Run tests only:** `pip install -e ".[dev]"` then `pytest tests/ -v`.

**Run app on host:** See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) Part 3.

## API overview

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/health` | Liveness |
| `POST /v1/chat` | Chat (request → decision → provider → audit → response) |
| `GET /v1/audit/{request_id}` | Audit event for a request (safe fields only) |
| `GET /v1/routes` | Effective routing policy (read-only; no secrets) |
| `GET /v1/metrics` | Prometheus metrics |

OpenAPI docs at `/docs` when the app is running. Config is via environment variables; see [.env.example](.env.example) and the [Getting started](docs/GETTING_STARTED.md) guide.

## Documentation

| Doc | Contents |
|-----|----------|
| **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** | Prerequisites, Docker flow, migrations, verification, troubleshooting |
| **[docs/ENGINE_RULES.md](docs/ENGINE_RULES.md)** | Routing policy: rule order, env variables, and how they affect behavior |
| **[docs/API_USAGE.md](docs/API_USAGE.md)** | Request/response contract, curl examples, integration snippet |
| **[docs/CONFIGURATION_SCENARIOS.md](docs/CONFIGURATION_SCENARIOS.md)** | Common setups: OpenAI default + sensitive local, local only, USD cost, audit off |
| **[docs/METRICS.md](docs/METRICS.md)** | Prometheus metrics, labels, scrape config, example queries |
| **[docs/PRIVACY.md](docs/PRIVACY.md)** | What we store (audit), what is sent to providers, controlling data flow |
| **[.env.example](.env.example)** | All env vars with short descriptions |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System design, request lifecycle, boundaries |
| **[docs/DECISIONS.md](docs/DECISIONS.md)** | Decision log and dependency choices |
| **[.context/](.context/)** | Task backlog, scope, and workflow (see [.context/README.md](.context/README.md)) |

## Development

- Tasks are tracked in [.context/TASKS.md](.context/TASKS.md); implementation follows the workflow in [.context/AGENTS.md](.context/AGENTS.md).
- CI: [.github/workflows/](.github/workflows/) — tests, container smoke.
