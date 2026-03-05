# Scope

## Purpose
Define what is in scope and out of scope so humans and AI agents can make consistent scope decisions. Use this file to prevent scope creep and resolve boundary questions quickly.

## In scope (current)
- **Endpoints:** `/v1/health`, `/v1/chat`, `/v1/metrics`, `/v1/routes`, `/v1/audit/{request_id}`
- **Routing:** Deterministic routing between `local` (configurable local LLM), `openai` (OpenAI), and `anthropic` (Anthropic); sensitivity (keywords) and cost (length or USD threshold) rules; configurable default provider
- **Providers:** Local LLM via `LOCAL_LLM_URL` (default Ollama-compatible); public/cloud via `PUBLIC_LLM_URL` with provider inferred from URL (OpenAI or Anthropic); API keys: `LOCAL_LLM_API_KEY` (optional), `PUBLIC_LLM_API_KEY`
- **Policy:** Policy (sensitivity, cost) from file only: `POLICY_FILE` must be set and the file must exist and be valid, else the application errors. Env is not a policy source. Schema extensible for future policy types (e.g. capability)
- **Audit:** One audit event per chat request in Postgres (prompt hash and metadata only; no raw prompts)
- **Observability:** Structured logs and Prometheus-compatible metrics
- **API:** OpenAPI interactive docs at `/docs`
- **UI:** Minimal static HTML/JS at `/` and `/ui` (chat, show rules, fetch audit for last request)

## Out of scope
- RAG and vector database
- Multi-tenant auth
- Caching beyond optional in-memory
- Additional providers beyond local + OpenAI + Anthropic
- Agent workflows
- Fancy or rich UI

## Security constraints
- Do not store raw prompts by default
- Store prompt hash + metadata (length, flags) only in audit
- Track failure categories in audit events

## Performance expectations
- Health endpoint is fast and stable
- Routing decisions are deterministic and low-latency
- Provider timeouts are explicit
