# Rules

## Purpose
Define the non-negotiable engineering guardrails for V1 execution. This is the canonical, tracked rules document for humans and AI agents.

## Authority
- `.context/RULES.md` is the canonical source of truth.
- `.context/private/RULES.md` may contain supplemental local/operator notes only.
- Private notes must not override or conflict with this document.

## 1) Scope Discipline
- Only tasks listed in `.context/TASKS.md` may be implemented.
- One task at a time: one task = one PR-sized, reviewable change.
- No scope creep beyond V1.
- Explicitly out of scope for V1:
  - RAG
  - Tenancy/auth
  - Multi-provider beyond local + OpenAI
  - Caching
  - Streaming
  - UI expansion
- No new endpoints, services, or modules unless explicitly required by the active task.
- No speculative implementation or future-proofing hooks.
- No broad abstractions in V1 unless they provide immediate value.

## 2) Change Management & Git Hygiene
- Keep changes patch-sized and reversible.
- No drive-by refactors; refactors require a dedicated task.
- Do not rename or remove files unless required by the task.
- Every feature must have a commit.
- Use conventional commit prefixes and include task ID (example: `feat(router): add sensitivity rule (T-102)`).
- No WIP commits on `main`.

## 3) Contracts & Interfaces
- All API request/response models must use Pydantic schemas.
- Public API schemas are contracts.
- If public API schemas change, update:
  - Tests
  - `README.md`
  - `docs/ARCHITECTURE.md`
- Feature implementations must update relevant documentation as applicable (for example: `README.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/STRUCTURE.md`, and task docs).
- Every interface is considered stable.
- Changes must be backward-compatible or explicitly approved.
- Every routing decision must include explicit reason codes.
- No magic outcomes.

## 4) Routing & Determinism
- Routing must be deterministic: same input + same config = same decision.
- Default routing behavior must be documented in `README.md` and/or `docs/ENGINE_RULES.md`.
- Any routing rule change requires a DecisionEngine unit test.
- Thresholds must be configurable (no hard-coded limits).

## 5) Audit, Logging & Observability
- Persist an audit event for every chat request.
- Never persist raw prompts.
- Store hash, length, and metadata flags only.
- Logs must be structured JSON.
- Expose Prometheus-compatible metrics.
- Any new feature must add or adjust at least one of:
  - A log field
  - A metric
  - An audit column

## 6) Security & Data Handling
- Secrets must never appear in code or logs.
- Use environment variables.
- Redact tokens.
- No PII in test fixtures.

## 7) Dependencies
- No new dependency without:
  - Adding an entry in `docs/DECISIONS.md`
  - Documenting why, alternatives considered, and risks

## 8) Testing Standards
- Every feature must include tests, or document why it cannot be tested.
- Provider calls must be mocked in tests.
- No real network calls in tests.
- Unit tests must be fast (`<1s` each).
- Provider changes require integration tests (mocked HTTP).
- When a task introduces a new runtime execution path (for example container, compose, or service startup behavior), CI coverage for that path must be added in the same task or tracked as an explicit follow-up task before the source task is considered fully closed.
- **When a task adds or expands the automated test suite, CI must run those tests.** Add or update the CI workflow (e.g. run pytest in the python-tests job) in the same task or as an explicit follow-up task before the source task is considered fully closed. A task that introduces tests is not done until CI executes them.

## 9) Agent Operating Rules
- Agents may only work on listed tasks.
- Agents must not expand scope.
- Planner role is documentation/scope-only; implementation changes must be performed by the Implementer role.
- **Planner must generate detailed prompts for the Coder and Tester agents and embed those prompts in the task file** (`.context/private/tasks/T-XXXX.md`) so handoff is self-contained; each role reads copy-paste-ready instructions from the task doc.
- Planner must not modify implementation/config files (including CI workflows, scripts, and runtime code) unless the user explicitly approves an exception for that session.
- Every agent response must include:
  - Task ID
  - Exact files changed
  - How to run tests/commands
  - Remaining work or follow-ups
  - Scope concerns (if any)

### Stop Conditions (Mandatory)
Agents must stop and ask if:
- A change requires a new dependency
- A new endpoint/module is implied but not listed
- Requirements are ambiguous
- Security or audit schema is affected
- Refactoring would impact more than ~5 files

When unsure: stop, do not guess.

## 10) Task Definition & Lifecycle
- Every task in `.context/TASKS.md` must include: why, in-scope items, out-of-scope items, files expected to change, test requirements, and definition of done.
- Every task must include a status field.
- When work is complete, mark the task status as `done`.
- Once the Coder and Tester outputs have been validated (acceptance criteria met, task doc updated), record completion in the task doc and `.context/TASKS.md`, then perform a **git commit** for the completed task (one task = one commit).
- Completed tasks must be archived under `.context/private/`.
