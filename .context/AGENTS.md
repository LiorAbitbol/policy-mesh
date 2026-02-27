# Agents

## Purpose
Define the canonical role model and workflow for AI-assisted development sessions in this repository.

## Authority
- `.context/AGENTS.md` is the canonical tracked source of truth for role boundaries and workflow.
- `.context/private/AGENTS.md` may include supplemental local/operator notes only.
- Private notes must not override or conflict with this document.

## Role Definitions

The three roles below are fulfilled by AI agents (any compatible model or tool). Names are role-based, not tied to a specific LLM or product.

## 1. Planner

**Responsibility**
- Break down work into tasks with explicit scope.
- Define acceptance criteria.
- Identify risks and non-goals.
- Update architecture/process documentation when necessary.

**May modify**
- `.context/TASKS.md`
- `.context/SCOPE.md`
- `.context/RULES.md`
- `.context/AGENTS.md`
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

## 2. Coder

**Responsibility**
- Implement exactly one task at a time.
- Make minimal, targeted changes.
- Follow acceptance criteria precisely.

**Pre-handoff hygiene**
- Before filling the Coding Update block or handing off to the tester, run the project's whitespace/style check (at minimum `git diff --check`) and fix trivial issues (trailing spaces, extra blank line at EOF, etc.) so the diff is clean.
- Ensure the working tree is clean and all tests relevant to the task are passing.

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

**Write the above into the task doc:** Before finishing, update `.context/private/tasks/T-XXXX.md` and fill in the **Coding Update (Coding Agent)** block (Date, Files changed, Assumptions, Run commands, What was intentionally not implemented). Include an **Assumptions** line (or "Assumptions (Coder):") listing any assumptions made so the Planner and Tester have them on the record. This is the handoff to the Planner and Tester.

One task = one commit-sized change.

## 3. Tester

**Responsibility**
- Validate implementation against acceptance criteria.
- Add or update tests.
- Identify edge cases and defects.
- Ensure deterministic behavior.

**Task doc responsibilities**
- Testing work is **not considered complete** until the tester has:
  - Filled in the **Testing Update (Testing Agent)** block in `.context/private/tasks/T-XXXX.md` (Date, Commands run, Results, Defects found, Acceptance checklist verification).
  - Set **Final Disposition → Final Status** to `done` or `blocked`, with any remaining follow-ups or scope concerns noted.

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

**Write the above into the task doc:** Before finishing, update `.context/private/tasks/T-XXXX.md`: fill in the **Testing Update (Testing Agent)** block (Date, Commands run, Results, Defects found, Acceptance checklist verification) and set **Final Disposition → Final Status** to `done` or `blocked`. This is the handoff to the Planner.

## Workflow
1. Planner defines task.
2. Coder implements task.
3. Tester validates task.
4. If defects are found, Coder fixes within task scope.
5. Task is complete when validation checklist passes.
6. Once Coder and Tester are validated, record completion in the task doc and `.context/TASKS.md`, then perform a **git commit** for the completed task (one task = one commit).

No role may expand scope without creating a new task.

## Session Isolation (Required)
For each task, use three separate AI sessions:
1. Planner session (task definition and scope only)
2. Coding session (implementation only)
3. Testing/review session (validation only)

Do not reuse one session for multiple roles in the same task.

Each role session must consume the prior role's handoff from `.context/private/tasks/T-XXXX.md` and append its own update block.

## Handoff to Planner (automated via task doc)
**Default (automated):** Coder and Tester **must** write their output into the task doc (Coding Update / Testing Update blocks and, for Tester, Final Disposition). The user then only says e.g. **"Coder done for T-112"** or **"Tester done for T-112"** or **"Both done for T-112"**. The Planner reads `.context/private/tasks/T-XXXX.md`, records any missing details if needed, updates `.context/TASKS.md`, and completes the workflow (e.g. git commit). No paste required.

**Fallback:** If the task doc could not be updated (e.g. Coder/Tester ran in an environment without write access to `.context/private/`), paste the agent’s output (assumptions, notes, files changed, run commands) into the Planner session. The Planner will record it in the task doc and proceed.

The Planner does not see other agents’ sessions; handoff is via the task doc or explicit paste.

## Stop Conditions (All Roles)
Stop and request clarification if:
- A change requires a new dependency
- The task implies adding endpoints not listed
- A schema change affects external API contracts
- More than ~5 files must change unexpectedly
- Security or audit logging is impacted

When in doubt: stop, do not guess.