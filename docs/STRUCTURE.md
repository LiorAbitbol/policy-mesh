# Project Structure (V1)

## Purpose
Provide an annotated directory tree so humans and AI agents can place code and docs consistently.
This represents the target V1 layout; some files/directories may be created incrementally as tasks are completed.

## Annotated Tree

```text
policy-mesh/
├── .github/
│   └── workflows/                   # GitHub Actions automation
│       └── ci.yml                   # Baseline CI for PR/push checks
├── alembic.ini                      # Alembic migration tool configuration
├── app/                             # Runtime application code (FastAPI service)
│   ├── main.py                      # App bootstrap and route registration
│   ├── api/                         # HTTP API layer
│   │   ├── deps.py                  # Shared API dependencies
│   │   ├── schemas/                 # Pydantic request/response contracts
│   │   │   ├── chat.py              # /v1/chat request/response models
│   │   │   └── common.py            # Shared schema fragments
│   │   └── routes/                  # Route handlers only (no core business logic)
│   │       ├── health.py            # /v1/health endpoint
│   │       ├── chat.py              # /v1/chat endpoint
│   │       ├── routes.py            # /v1/routes endpoint
│   │       └── metrics.py           # /v1/metrics endpoint
│   ├── core/                        # Cross-cutting app internals
│   │   ├── config.py                # Environment-driven settings
│   │   ├── logging.py               # Structured JSON logging setup
│   │   └── telemetry.py             # Metrics/logging wiring helpers
│   ├── decision/                    # Deterministic routing policy engine
│   │   ├── engine.py                # Decision orchestration logic
│   │   ├── policies.py              # Cost/sensitivity policy checks
│   │   └── reason_codes.py          # Explicit decision reason code definitions
│   ├── providers/                   # Provider adapters (local + openai only in V1)
│   │   ├── base.py                  # Shared provider interface contract
│   │   ├── ollama.py                # Ollama client adapter
│   │   └── openai.py                # OpenAI client adapter
│   ├── audit/                       # Audit model and persistence logic
│   │   ├── models.py                # AuditEvent model(s)
│   │   ├── repository.py            # Audit persistence adapter
│   │   └── service.py               # Audit write orchestration helpers
│   └── services/                    # Application orchestration services
│       └── chat_orchestrator.py     # /v1/chat flow: decision -> provider -> audit -> metrics
├── tests/                           # Automated tests (no real network calls)
│   ├── unit/                        # Fast, isolated unit tests
│   │   ├── test_decision_engine.py  # Decision branch/determinism tests
│   │   └── test_reason_codes.py     # Reason code contract tests
│   ├── integration/                 # Request flow and adapter integration tests (mocked HTTP)
│   │   ├── test_chat_flow.py        # End-to-end API flow tests
│   │   ├── test_providers.py        # Provider adapter integration tests
│   │   ├── test_audit.py            # Audit persistence integration tests
│   │   └── test_metrics.py          # Metrics endpoint/instrumentation tests
│   └── fixtures/                    # Test fixtures (no PII/secrets)
│       └── sample_requests.py       # Reusable request payload fixtures
├── scripts/                         # Local helper scripts for run/smoke tasks
│   ├── run_local.sh                 # Start service in local dev mode
│   └── smoke.sh                     # Quick local smoke checks
├── docs/                            # Technical docs (public repo docs)
│   ├── STRUCTURE.md                 # This file: annotated project tree
│   ├── ARCHITECTURE.md              # Architecture rationale and system flows
│   └── DECISIONS.md                 # Dependency/engineering decision log
├── migrations/                      # Alembic migration environment and revisions
│   ├── env.py                       # Alembic migration runtime setup
│   └── versions/                    # Versioned migration scripts
├── context/                         # Public execution contract and backlog
│   ├── README.md                    # Context usage and contract overview
│   ├── PROJECT.md                   # Product goals and architecture summary
│   ├── SCOPE.md                     # In-scope/out-of-scope definition
│   ├── TASKS.md                     # Active task index and status board
│   ├── RULES.md                     # Public pointer to private rules source
│   ├── AGENTS.md                    # Public pointer to private workflow source
│   └── private/                     # Canonical internal playbooks and task records
│       ├── README.md                # Private docs purpose and source-of-truth map
│       ├── RULES.md                 # Canonical non-negotiable rules
│       ├── AGENTS.md                # Canonical role/session workflow
│       ├── tasks/                   # Canonical per-task execution docs
│       │   └── T-XXXX.md            # Planner/Coder/Tester handoff record
│       └── archive/                 # Completed task history
│           └── README.md            # Archival conventions
├── Dockerfile                       # App container image definition
├── .dockerignore                    # Build context exclusions
├── docker-compose.yml               # Local demo orchestration
├── .env.example                     # Documented environment variables template
├── pyproject.toml                   # Python project/tooling configuration
└── README.md                        # Top-level project overview and run instructions
```

## Conventions
- Place new files in the smallest existing module that matches the task scope.
- Keep API contracts in `app/api/schemas/`; update tests and docs for public schema changes.
- Keep routing policy logic in `app/decision/` and provider logic in `app/providers/`.
- Keep task execution details in `context/private/tasks/`; keep `context/TASKS.md` concise.
- Keep tests deterministic and isolated; do not use real provider network calls.
- Keep CI workflow logic in `.github/workflows/` and expand checks task-by-task.

## V1 Guardrails for Structure Changes
- Do not add RAG/vector, multi-tenant auth, or extra providers in V1.
- Do not introduce new top-level modules/endpoints unless required by an active task.
- Prefer minimal, reviewable additions over broad abstractions.
