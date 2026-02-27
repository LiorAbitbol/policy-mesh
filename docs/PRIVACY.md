# Privacy and data

This document summarizes what data Policy Mesh stores, what is sent to which provider, and how to control it.

---

## What the app stores (audit)

When audit is enabled (`DATABASE_URL` set and `AUDIT_ENABLED` not set to `false`), the app persists **one audit event per chat request** in Postgres.

**Stored fields:**

- **request_id** — Unique ID for the request (for traceability).
- **decision** — Which provider was chosen and why (e.g. `provider=openai,reason_codes=default_openai`).
- **status** — `success` or `failure`.
- **latency_ms** — End-to-end provider latency.
- **failure_category** — Normalized failure category when the provider call failed.
- **prompt_hash** — A hash of the prompt text. **Raw prompt text is not stored.**
- **prompt_length** — Length of the prompt in characters.
- **created_at** — Timestamp.

**Not stored:** Raw prompt content, raw model replies, API keys, or any PII beyond what you put in the prompt (and we only store a hash of the prompt, not the text).

Audit is intended for compliance, debugging, and usage analysis without retaining the actual conversation content.

---

## What is sent to providers

- **Local (Ollama):** The prompt (and conversation history in the request) is sent to your Ollama instance. Data stays on your machine or your Docker network.
- **OpenAI:** The prompt (and conversation history) is sent to the OpenAI API according to their [data usage policies](https://openai.com/policies/usage-policies). We do not log or persist the raw prompt or response; we only persist the audit fields listed above.

Routing is determined by the [engine rules](ENGINE_RULES.md). Use **sensitivity keywords** to route prompts that mention sensitive topics to local only, so that text never reaches the cloud.

---

## Controlling data flow

| Goal | How |
|------|-----|
| **Keep sensitive prompts off the cloud** | Set `SENSITIVITY_KEYWORDS` so that prompts containing those words route to local. See [Engine rules](ENGINE_RULES.md) and [Configuration scenarios](CONFIGURATION_SCENARIOS.md). |
| **Disable audit** | Set `AUDIT_ENABLED=false` in `.env`. No audit events are written. |
| **Run without a database** | Do not set `DATABASE_URL`, or set `AUDIT_ENABLED=false` if you have a DB for other reasons. |

Secrets (e.g. `OPENAI_API_KEY`) are read from the environment only; they are not logged or exposed in API responses. The `/v1/routes` endpoint returns the effective routing policy but never exposes keyword values or secrets.
