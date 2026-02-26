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

## Documentation Map
- `docs/STRUCTURE.md` - Annotated project tree and placement conventions.
- `docs/ARCHITECTURE.md` - V1 architecture, request lifecycle, boundaries.
- `docs/DECISIONS.md` - Decision log and dependency decision template.

## Context and Workflow
- `context/` contains public execution context (`PROJECT`, `SCOPE`, `TASKS`) and pointers.
- `context/private/` contains canonical internal playbooks and task records.
- AI-assisted development is used; detailed operational workflows are intentionally maintained in private docs.

## CI
- Planned in task `T-108` (`context/TASKS.md`).
- Not implemented yet in the current repository state.

## Repository Layout (Top Level)
- `.github/` - CI workflows.
- `context/` - Public project context and pointers.
- `docs/` - Architecture, structure, and decisions.
- `README.md` - This file.

## Next Steps
- Implement tasks in `context/TASKS.md` in order.
- Keep one task per PR-sized change.
- Update tests and docs with any interface or behavior changes.
