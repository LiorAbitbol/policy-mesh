# Tasks

## Purpose
Provide the executable public backlog for V1.
Each task links to a private canonical task document with full planning, coding, and testing updates.

## Status Model
- `todo` = not started
- `in_progress` = actively being worked
- `blocked` = waiting for clarification, dependency, or decision
- `done` = implementation and validation complete

## Current Milestone
M1: Runnable vertical slice (`/v1/chat` -> decision -> provider -> audit -> metrics)

## Current Status Snapshot
- Last Updated: 2026-02-26
- Done: `T-108` (Add GitHub Actions CI baseline), `T-101` (Bootstrap FastAPI app and `/v1/health`), `T-110` (Add app container layer and healthcheck wiring), `T-111` (Add CI container smoke validation for app service), `T-109` (Add local Postgres setup and migration bootstrap)
- In Progress: none
- Next: `T-104` (Persist `AuditEvent` per request)

## Task Summary
| Execution Order | Task ID | Title | Status | Owner Role | Private Task Doc |
|---|---|---|---|---|---|
| 1 | T-108 | Add GitHub Actions CI baseline | `done` | `planner` | `context/private/tasks/T-108.md` |
| 2 | T-101 | Bootstrap FastAPI app and `/v1/health` | `done` | `planner` | `context/private/tasks/T-101.md` |
| 3 | T-110 | Add app container layer and healthcheck wiring | `done` | `planner` | `context/private/tasks/T-110.md` |
| 4 | T-111 | Add CI container smoke validation for app service | `done` | `planner` | `context/private/tasks/T-111.md` |
| 5 | T-109 | Add local Postgres setup and migration bootstrap | `done` | `planner` | `context/private/tasks/T-109.md` |
| 6 | T-104 | Persist `AuditEvent` per request | `todo` | `planner` | `context/private/tasks/T-104.md` |
| 7 | T-102 | Implement DecisionEngine with reason codes | `todo` | `planner` | `context/private/tasks/T-102.md` |
| 8 | T-103 | Implement Ollama and OpenAI provider clients | `todo` | `planner` | `context/private/tasks/T-103.md` |
| 9 | T-105 | Add `/v1/chat` orchestration service | `todo` | `planner` | `context/private/tasks/T-105.md` |
| 10 | T-106 | Add metrics middleware + `/v1/metrics` | `todo` | `planner` | `context/private/tasks/T-106.md` |
| 11 | T-107 | Add integration tests with mocked providers | `todo` | `planner` | `context/private/tasks/T-107.md` |

## Task Index
- T-101: Bootstrap FastAPI app and `/v1/health`
  - Status: `done`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-101.md`
  - Acceptance: App starts and health endpoint returns 200.
- T-108: Add GitHub Actions CI baseline
  - Status: `done`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-108.md`
  - Acceptance: PR/push workflow runs repo checks now and is ready to expand for Python tests.
- T-110: Add app container layer and healthcheck wiring
  - Status: `done`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-110.md`
  - Acceptance: Docker image runs app and containerized health check verifies `/v1/health`.
- T-111: Add CI container smoke validation for app service
  - Status: `done`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-111.md`
  - Acceptance: CI builds app container, runs compose app service, and validates `/v1/health` smoke checks.
- T-109: Add local Postgres setup and migration bootstrap
  - Status: `done`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-109.md`
  - Acceptance: Local Postgres is runnable via docker-compose with env config and migration bootstrap path documented.
- T-104: Persist `AuditEvent` per request
  - Status: `todo`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-104.md`
  - Acceptance: DB row includes request id, decision, status, latency.
- T-102: Implement DecisionEngine with reason codes
  - Status: `todo`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-102.md`
  - Acceptance: Unit tests cover sensitive/cost/default branches.
- T-103: Implement Ollama and OpenAI provider clients
  - Status: `todo`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-103.md`
  - Acceptance: Both providers callable via shared interface.
- T-105: Add `/v1/chat` orchestration service
  - Status: `todo`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-105.md`
  - Acceptance: Endpoint returns provider, reasons, response payload.
- T-106: Add metrics middleware + `/v1/metrics`
  - Status: `todo`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-106.md`
  - Acceptance: Counters and latency histograms exposed.
- T-107: Add integration tests with mocked providers
  - Status: `todo`
  - Owner Role: `planner`
  - Private Task Doc: `context/private/tasks/T-107.md`
  - Acceptance: Tests verify route, fallback behavior, and audit write.
