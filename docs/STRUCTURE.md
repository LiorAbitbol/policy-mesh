# Project Structure

## Purpose
Provide an annotated directory tree so humans and AI agents can place code and docs consistently.
The tree below reflects the current layout (M1 + M2 implemented).

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
│   │   ├── schemas/                 # Pydantic request/response contracts
│   │   │   ├── chat.py             # /v1/chat request/response models
│   │   │   ├── audit.py            # Audit event view (GET /v1/audit/{id})
│   │   │   └── routes.py           # Effective policy view (GET /v1/routes)
│   │   └── routes/                  # Route handlers only (no core business logic)
│   │       ├── health.py            # /v1/health endpoint
│   │       ├── chat.py              # /v1/chat endpoint
│   │       ├── metrics.py           # /v1/metrics endpoint
│   │       ├── audit.py             # GET /v1/audit/{request_id}
│   │       └── routes.py            # GET /v1/routes (effective policy)
│   ├── core/                        # Cross-cutting app internals
│   │   ├── config.py                # Environment-driven settings
│   │   └── telemetry.py             # Metrics (Prometheus) and recording
│   ├── decision/                    # Deterministic routing policy engine
│   │   ├── engine.py                # Decision orchestration logic
│   │   ├── policies.py              # Cost/sensitivity policy checks
│   │   └── reason_codes.py          # Explicit decision reason code definitions
│   ├── providers/                   # Provider adapters (Ollama + OpenAI)
│   │   ├── base.py                  # Shared provider interface contract
│   │   ├── ollama.py                # Ollama client adapter
│   │   └── openai.py                # OpenAI client adapter
│   ├── audit/                       # Audit model and persistence logic
│   │   ├── models.py                # AuditEvent model(s)
│   │   ├── context.py               # Async session/engine setup for audit
│   │   ├── repository.py            # Audit persistence adapter
│   │   └── service.py               # Audit write orchestration helpers
│   ├── static/                      # Minimal UI (T-203): single-page static HTML/JS
│   │   └── index.html               # Chat, rules (GET /v1/routes), audit (GET /v1/audit/{id})
│   └── services/                    # Application orchestration services
│       └── chat_orchestrator.py     # /v1/chat flow: decision -> provider -> audit -> metrics
├── tests/                           # Automated tests (no real network calls)
│   ├── unit/                        # Fast, isolated unit tests
│   │   ├── test_decision_engine.py  # Decision branch/determinism tests
│   │   ├── test_reason_codes.py     # Reason code contract tests
│   │   └── test_audit.py            # Audit model/repository unit tests
│   └── integration/                 # Request flow and adapter integration tests (mocked HTTP)
│       ├── test_chat_flow.py        # End-to-end API flow tests
│       ├── test_providers.py        # Provider adapter integration tests
│       ├── test_audit.py            # Audit persistence integration tests
│       ├── test_audit_endpoint.py   # GET /v1/audit/{id} endpoint tests
│       ├── test_metrics.py          # Metrics endpoint/instrumentation tests
│       ├── test_health.py           # Health endpoint tests
│       ├── test_routes_endpoint.py  # GET /v1/routes endpoint tests
│       └── test_ui.py               # UI static serving and paths
├── docs/                            # Technical docs (public repo docs)
│   ├── GETTING_STARTED.md           # Prerequisites and step-by-step run/tests guide
│   ├── STRUCTURE.md                 # This file: annotated project tree
│   ├── ARCHITECTURE.md              # System design, tech stack, flows, boundaries
│   ├── DECISIONS.md                 # Dependency/engineering decision log
│   ├── ENGINE_RULES.md              # Routing policy: rule order, env vars, behavior
│   ├── API_USAGE.md                 # Request/response contract, curl examples
│   ├── CONFIGURATION_SCENARIOS.md   # Common .env setups (OpenAI default, local only, etc.)
│   ├── METRICS.md                  # Prometheus metrics, scrape config, example queries
│   └── PRIVACY.md                  # What we store (audit), what is sent to providers
├── migrations/                      # Alembic migration environment and revisions
│   ├── env.py                       # Alembic migration runtime setup
│   └── versions/                    # Versioned migration scripts
├── .context/                        # Execution contract and backlog (tracked)
│   ├── README.md                    # Context usage and contract overview
│   ├── PROJECT.md                   # Short pointer to product and current state
│   ├── SCOPE.md                     # In-scope/out-of-scope definition
│   ├── TASKS.md                     # Active task index and status board
│   ├── RULES.md                     # Canonical engineering guardrails
│   ├── AGENTS.md                    # Canonical role model and workflow
│   └── private/                     # Task records, planner prompt, retrospect (gitignored)
│       ├── README.md                # Private folder purpose; canonical = parent .context/
│       ├── RULES.md                 # Supplemental local/operator notes only
│       ├── AGENTS.md                # Supplemental local/operator notes only
│       ├── PROMPT.md                # Planner agent prompt and workflow
│       ├── RETROSPECT.md            # Process lessons and starter checklist for next project
│       ├── tasks/                   # Per-task execution docs (handoffs, updates)
│       │   └── T-XXXX.md            # Planner/Coder/Tester handoff record
│       └── archive/                  # Completed task history
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
- Keep task execution details in `.context/private/tasks/`; keep `.context/TASKS.md` concise.
- Keep tests deterministic and isolated; do not use real provider network calls.
- Keep CI workflow logic in `.github/workflows/` and expand checks task-by-task.

## Guardrails for Structure Changes
- Do not add RAG/vector, multi-tenant auth, or extra providers unless in scope (see `.context/SCOPE.md`).
- Do not introduce new top-level modules/endpoints unless required by an active task.
- Prefer minimal, reviewable additions over broad abstractions.
