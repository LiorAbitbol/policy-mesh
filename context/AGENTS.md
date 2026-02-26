# Agents

## Purpose
Define the canonical role model and workflow for AI-assisted development sessions in this repository.

## Authority
- `context/AGENTS.md` is the canonical tracked source of truth for role boundaries and workflow.
- `context/private/AGENTS.md` may include supplemental local/operator notes only.
- Private notes must not override or conflict with this document.

## Role Definitions

## 1. Codex - Planner / Reasoning Role

**Responsibility**
- Break down work into tasks with explicit scope.
- Define acceptance criteria.
- Identify risks and non-goals.
- Update architecture/process documentation when necessary.

**May modify**
- `context/TASKS.md`
- `context/SCOPE.md`
- `context/RULES.md`
- `context/AGENTS.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`

**Must NOT**
- Modify production code (`app/**`)
- Modify tests (`tests/**`)
- Add dependencies directly
- Modify implementation/config files (for example: `.github/workflows/**`, `scripts/**`, runtime/config files) unless the user explicitly approves an exception for that session

**Output Requirements**
Every task definition/handoff must include:
- Task ID
- Title
- Scope (explicit bullet list)
- Out-of-scope items
- Files expected to change
- Acceptance criteria checklist
- Test requirements
- Stop conditions

## 2. Cursor - Implementer / Coding Role

**Responsibility**
- Implement exactly one task at a time.
- Make minimal, targeted changes.
- Follow acceptance criteria precisely.

**May modify**
- Implementation/config files required by the active task (for example: `app/**`, `.github/workflows/**`, `scripts/**`, `docker-compose.yml`, and task-required docs)

**Must NOT**
- Change scope
- Add new features not in task
- Introduce new dependencies without a decision entry
- Perform unrelated refactors
- Modify tests unless explicitly required by task

**Output Requirements**
Each implementation must include:
- Task ID
- Files changed (explicit list)
- How to run/test locally
- Assumptions made
- Explicit statement of what was intentionally NOT implemented

One task = one commit-sized change.

## 3. Claude - Testing / Validation Role

**Responsibility**
- Validate implementation against acceptance criteria.
- Add or update tests.
- Identify edge cases and defects.
- Ensure deterministic behavior.

**May modify**
- `tests/**`
- Minor testability fixes if explicitly allowed in the active task

**Must NOT**
- Introduce new features
- Modify architecture
- Add new endpoints or providers
- Expand scope beyond the task

**Validation Checklist**
- Acceptance criteria satisfied
- Deterministic routing behavior verified
- No real network calls in tests
- Schema contracts respected
- No raw prompt persistence
- Metrics/logging not broken

## Workflow
1. Codex defines task.
2. Cursor implements task.
3. Claude validates task.
4. If defects are found, Cursor fixes within task scope.
5. Task is complete when validation checklist passes.
6. Once Coder and Tester are validated, record completion in the task doc and `context/TASKS.md`, then perform a **git commit** for the completed task (one task = one commit).

No role may expand scope without creating a new task.

## Session Isolation (Required)
For each task, use three separate AI sessions:
1. Planner session (task definition and scope only)
2. Coding session (implementation only)
3. Testing/review session (validation only)

Do not reuse one session for multiple roles in the same task.

Each role session must consume the prior role's handoff from `context/private/tasks/T-XXXX.md` and append its own update block.

## Stop Conditions (All Roles)
Stop and request clarification if:
- A change requires a new dependency
- The task implies adding endpoints not listed
- A schema change affects external API contracts
- More than ~5 files must change unexpectedly
- Security or audit logging is impacted

When in doubt: stop, do not guess.