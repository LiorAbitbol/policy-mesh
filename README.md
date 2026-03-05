# Policy Mesh

A local-first AI gateway that routes chat requests between local and cloud providers based on configurable policy, with audit, metrics, and a minimal UI.

## Tech stack

**Python 3.11+**, **FastAPI**, **PostgreSQL**, **Ollama** (local LLM), **OpenAI** and **Anthropic** (cloud). Run with **Docker Compose** or on the host. See [docs/architecture.md](docs/architecture.md) for the full stack, request process flow, and decision flow diagrams.

## What it does

- **Routes** each request deterministically: sensitivity (keywords) → cost (length or USD threshold) → default provider.
- **Supports** local LLM (e.g. Ollama) and cloud (OpenAI, Anthropic). Every decision returns explicit reason codes.
- **Persists** one audit event per chat (prompt hash and metadata only; no raw prompts).
- **Exposes** Prometheus-compatible metrics and a read-only view of the effective routing policy (`/v1/routes`).
- **Serves** a minimal static UI at `/` and `/ui` for chat, rules, and audit.

## Quick start

```bash
git clone https://github.com/LiorAbitbol/policy-mesh.git && cd policy-mesh
cp .env.example .env   # edit with your API key, set POLICY_FILE to your policy JSON path (see Policy file schema), and/or provider choices
```

**Run with Docker (recommended):** Postgres → migrations → app (and optionally Ollama). Full step-by-step: **[docs/getting_started.md](docs/getting_started.md)**.

**Run tests only:** `pip install -e ".[dev]"` then `pytest tests/ -v`.

**Run app on host:** See [docs/getting_started.md](docs/getting_started.md) Part 3.

## API overview

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/health` | Liveness |
| `POST /v1/chat` | Chat (request → decision → provider → audit → response) |
| `GET /v1/audit/{request_id}` | Audit event for a request (safe fields only) |
| `GET /v1/routes` | Effective routing policy (read-only; no secrets) |
| `GET /v1/metrics` | Prometheus metrics |

OpenAPI docs at `/docs` when the app is running. Config is via environment variables and a required policy file (**POLICY_FILE**); see [.env.example](.env.example), [Getting started](docs/getting_started.md), and [Policy file schema](docs/policy_file_schema.md).

## Documentation

| Doc | Contents |
|-----|----------|
| **[docs/getting_started.md](docs/getting_started.md)** | Prerequisites, Docker flow, migrations, verification, troubleshooting |
| **[docs/engine_rules.md](docs/engine_rules.md)** | Routing policy: rule order, policy file (POLICY_FILE), and how they affect behavior |
| **[docs/policy_file_schema.md](docs/policy_file_schema.md)** | Policy file JSON schema and location |
| **[docs/policies.example.json](docs/policies.example.json)** | Example policy file |
| **[docs/api_usage.md](docs/api_usage.md)** | Request/response contract, curl examples, integration snippet |
| **[docs/configuration_scenarios.md](docs/configuration_scenarios.md)** | Common setups: OpenAI default + sensitive local, local only, USD cost, audit off |
| **[docs/metrics.md](docs/metrics.md)** | Prometheus metrics, labels, scrape config, example queries |
| **[docs/privacy.md](docs/privacy.md)** | What we store (audit), what is sent to providers, controlling data flow |
| **[.env.example](.env.example)** | All env vars with short descriptions |
| **[docs/architecture.md](docs/architecture.md)** | System design, request process flow, decision flow, boundaries |
| **[docs/decisions.md](docs/decisions.md)** | Decision log and dependency choices |
| **[.context/](.context/)** | Task backlog, scope, and workflow (see [.context/README.md](.context/README.md)) |

## Development

- Tasks are tracked in [.context/tasks.md](.context/tasks.md); implementation follows the workflow in [.context/agents.md](.context/agents.md).
- CI: [.github/workflows/](.github/workflows/) — tests, container smoke.
