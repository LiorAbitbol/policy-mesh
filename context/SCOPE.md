# Scope (V1)

## Purpose
Define what V1 includes and excludes so humans and AI agents can make consistent scope decisions. Use this file to prevent scope creep and resolve boundary questions quickly.

## In Scope
- FastAPI endpoints: `/v1/chat`, `/v1/health`, `/v1/routes`, `/v1/metrics`
- Deterministic routing between `local` and `openai`
- Cost and sensitivity-based policy decisions
- Audit event persistence
- Structured logs and Prometheus-compatible metrics
- Simple CLI and simple UI

## Out of Scope
- RAG and vector database
- Multi-tenant auth
- Caching beyond optional in-memory
- Additional providers beyond local + openai
- Agent workflows
- Fancy UI

## Security Constraints
- Do not store raw prompts by default
- Store prompt hash + metadata (length/flags)
- Track failure categories in audit events

## Performance Expectations (Basic)
- Health endpoint is fast and stable
- Routing decisions are deterministic and low-latency
- Provider timeouts are explicit
