# Scope (V1)

## Purpose
Define what V1 includes and excludes so humans and AI agents can make consistent scope decisions. Use this file to prevent scope creep and resolve boundary questions quickly.

## In Scope
- Implemented endpoints: `/v1/health`, `/v1/chat`, `/v1/metrics` (`/v1/routes` deferred)
- Deterministic routing between `local` and `openai`
- Cost and sensitivity-based policy decisions
- Audit event persistence (Postgres)
- Structured logs and Prometheus-compatible metrics
- API with OpenAPI interactive docs (`/docs`); CLI and simple UI deferred

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
