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
