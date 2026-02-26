# Project

## Problem Statement
Teams need a reliable local-first AI gateway that controls cost and risk while preserving auditability.

## V1 Objective
Ship a deterministic router that selects between local (Ollama) and cloud (OpenAI), records auditable decisions, and exposes baseline metrics.

## V1 Demo Script
1. Send prompt to `POST /v1/chat`
2. Show routing decision and reason codes
3. Return model response
4. Show audit record written
5. Show metrics incremented

## Architecture Summary
`Client -> API -> DecisionEngine -> Provider (Ollama/OpenAI) -> Audit -> Metrics`

## Key Modules
- DecisionEngine
- Providers (Ollama/OpenAI)
- Audit logging
- Telemetry (structured logs + metrics)

## What Good Looks Like (V1)
- Deterministic routing behavior
- No raw prompt storage by default
- Clear reason codes on every decision
- Repeatable local demo via docker-compose
