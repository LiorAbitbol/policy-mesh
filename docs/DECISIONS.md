# Decisions Log

## Purpose
Record architectural and engineering decisions for V1, including dependency choices and trade-offs.

## Status Values
- `proposed`
- `accepted`
- `superseded`
- `rejected`

---

## DEC-001: V1 Provider Scope
- Status: `accepted`
- Date: 2026-02-25

### Decision
V1 supports exactly two providers: local `ollama` and cloud `openai`.

### Why
- Meets local-first and cloud-fallback objective.
- Keeps adapter complexity small and reviewable in V1.

### Alternatives Considered
- Add more providers in V1.
- Local-only provider set.

### Risks
- Provider abstraction may need extension in future phases.
- Cloud fallback behavior must remain explicit and test-covered.

---

## DEC-002: Deterministic Policy Engine with Reason Codes
- Status: `accepted`
- Date: 2026-02-25

### Decision
Routing decisions must be deterministic and always return explicit reason codes.

### Why
- Enables reproducibility, auditability, and predictable behavior.
- Avoids opaque "magic" outcomes.

### Alternatives Considered
- Heuristic/non-deterministic routing.
- Decision outputs without reason-code contract.

### Risks
- Overly rigid rules may reduce flexibility for future experimentation.
- Reason-code taxonomy must remain stable over time.

---

## DEC-003: Prompt Privacy by Default
- Status: `accepted`
- Date: 2026-02-25

### Decision
Raw prompts are not persisted by default; store hash, length, and metadata flags only.

### Why
- Reduces privacy/security risk while preserving audit utility.
- Aligns with governance rules and minimal data retention posture.

### Alternatives Considered
- Store full prompt text for debugging.
- Opt-in raw prompt storage in V1.

### Risks
- Less direct debug context without raw prompt text.
- Hash/metadata design must be consistent and documented.

---

## DEC-004: CI Baseline via GitHub Actions
- Status: `accepted`
- Date: 2026-02-25

### Decision
Use GitHub Actions for baseline CI on pull requests and pushes to `main`.

### Why
- Native integration with repository workflows.
- Provides immediate quality gate and scalable automation path.

### Alternatives Considered
- External CI provider.
- No CI until app code is complete.

### Risks
- Baseline checks may be too weak early on if not expanded with code growth.
- CI changes should remain task-scoped and reviewable.

---

## DEC-005: Audit Event Persistence Backend for V1
- Status: `accepted`
- Date: 2026-02-25

### Decision
Persist audit events in a Postgres database table for V1, with a repository/service boundary to keep persistence swappable if future needs change.

### Why
- Provides durable, queryable, schema-consistent audit records.
- Aligns with V1 requirement to persist an audit event per request and capture decision/status/latency/failure details.

### Alternatives Considered
- SQLite-first for local/demo workflow.
- Structured logs only (no DB table).
- In-memory storage for demo-only use.

### Risks
- Local setup is heavier than SQLite-only development.
- Schema migration discipline is required as the model evolves.

---

## DEC-006: Migration Tooling - Alembic
- Status: `accepted`
- Date: 2026-02-25

### Decision
Use Alembic for database schema migrations in V1.

### Why
- Standard migration workflow for Python/Postgres stacks.
- Supports explicit, versioned schema evolution and repeatable upgrades.

### Alternatives Considered
- Hand-written SQL bootstrap scripts only.
- ORM auto-create without managed migrations.

### Risks
- Requires migration discipline to avoid drift between models and revision files.
- Adds tooling complexity if migration scripts are not kept task-scoped.

---

## DEC-007: FastAPI Bootstrap and Minimal Test Tooling
- Status: `accepted`
- Date: 2026-02-26

### Decision
Adopt `fastapi` and `uvicorn` as the minimal runtime stack for V1 API bootstrap, and `pytest` plus `httpx` as minimal development/testing dependencies for endpoint validation in T-101.

### Why
- Enables a deterministic, lightweight `/v1/health` API bootstrap aligned with V1 architecture.
- Establishes a reproducible local setup from fresh clone for running the app and integration-style health test.

### Alternatives Considered
- Delay dependency declaration until later tasks.
- Use a different web framework stack for initial endpoint bootstrap.

### Risks
- Early dependency choices may constrain future framework changes.
- Unpinned dependency ranges can introduce upstream behavior drift over time.

---

## DEC-008: Migration Stack Dependencies (Alembic, SQLAlchemy, psycopg)
- Status: `accepted`
- Date: 2026-02-26

### Decision
Add `alembic`, `sqlalchemy`, and `psycopg[binary]` as dev dependencies for running migrations against local Postgres (T-109).

### Why
- Alembic requires SQLAlchemy for metadata and migration generation.
- `psycopg` is the Postgres adapter for `postgresql://` URLs in Alembic.

### Alternatives Considered
- `psycopg2-binary` (legacy driver; psycopg3 is maintained and async-capable).
- Async-only driver for migrations (rejected: Alembic migrations are sync by default).

### Risks
- Driver version compatibility with Postgres 16; psycopg supports current Postgres versions.

---

## DEC-009: HTTP client for provider adapters (httpx)
- Status: `accepted`
- Date: 2026-02-26

### Decision
Add `httpx` as a runtime dependency for Ollama and OpenAI provider clients (T-103).

### Why
- Provider adapters need an HTTP client for POST requests to Ollama (/api/chat) and OpenAI (chat completions).
- httpx offers a sync API, configurable timeouts, and is easy to mock in tests (inject client or mock).

### Alternatives Considered
- `requests` (widely used; httpx has similar API and better async path if needed later).
- `urllib` only (more boilerplate and no built-in timeout abstraction).

### Risks
- Additional runtime dependency; keep version pinned in pyproject.toml to avoid drift.

---

## DEC-010: Runtime dependencies for audit (sqlalchemy, psycopg)
- Status: `accepted`
- Date: 2026-02-26

### Decision
Promote `sqlalchemy` and `psycopg[binary]` from dev extras to main (runtime) dependencies in pyproject.toml.

### Why
- The app imports `app.audit.repository` at startup (via chat route → chat_orchestrator → audit.service → audit.repository). That module imports SQLAlchemy and uses it when persisting audit events.
- With these only in `[dev]`, `pip install .` in the Docker image did not install them, so the app crashed on startup with ModuleNotFoundError and the container smoke test failed.
- Making them runtime deps ensures the container starts and the audit code path is loadable; when DATABASE_URL is not set, audit is a no-op.

### Alternatives Considered
- Lazy-import audit.repository only when persist_audit_event is called (adds complexity; still need sqlalchemy when audit is enabled).
- Keep audit in a separate optional extra (would require two container images or conditional installs).

### Risks
- Slightly larger runtime image; acceptable for V1.

---

## DEC-011: Prometheus client for metrics (prometheus_client)
- Status: `accepted`
- Date: 2026-02-26

### Decision
Use the `prometheus_client` Python package for Prometheus-compatible counters and histograms, and expose `/v1/metrics` returning the default registry in Prometheus text exposition format.

### Why
- Standard, widely used client; output is scrape-ready for Prometheus.
- Supports Counter and Histogram; low overhead and deterministic.
- No custom format to maintain.

### Alternatives Considered
- Custom plain-text format: no dependency but reinvents the wheel and may diverge from Prometheus expectations.
- OpenTelemetry: heavier and out of scope for V1 “Prometheus-compatible” requirement.

### Risks
- New runtime dependency; add to main deps in pyproject.toml. High-cardinality labels must be avoided (use only provider, status, not request_id or reason_codes).

---

## Dependency Decision Template
Use this template when introducing any new dependency.

```md
## DEC-XXX: <Dependency or Decision Title>
- Status: `proposed|accepted|superseded|rejected`
- Date: YYYY-MM-DD

### Decision
<What is being adopted or changed?>

### Why
- <Primary reason 1>
- <Primary reason 2>

### Alternatives Considered
- <Alternative A>
- <Alternative B>

### Risks
- <Risk 1 and mitigation>
- <Risk 2 and mitigation>
```
