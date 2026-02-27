# Project

## Purpose
One-page pointer to what Policy Mesh is and where to find details. Use this for quick orientation; for execution use TASKS, RULES, and AGENTS.

## What it is
A local-first AI gateway that routes chat requests between local (Ollama) and cloud (OpenAI) based on configurable policy, with audit, metrics, and a minimal UI.

## Where to read more
- **Product overview and quick start:** [README.md](../README.md) (repo root)
- **System design and request lifecycle:** [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Routing rules and env vars:** [docs/ENGINE_RULES.md](../docs/ENGINE_RULES.md)
- **Scope and boundaries:** [.context/SCOPE.md](SCOPE.md)
- **Backlog and status:** [.context/TASKS.md](TASKS.md)

## Current state
- M1 (vertical slice) and M2 (operator UX: request_id, audit fetch, `/v1/routes`, USD cost rule, minimal UI) are **done**.
- All tasks in TASKS.md are complete; new work is added there as new tasks.
