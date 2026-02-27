# Configuration scenarios

This page gives copy-paste `.env` snippets for common setups. For how each variable affects behavior, see [Engine rules](ENGINE_RULES.md). Start from [.env.example](../.env.example) and add or override only what’s listed below.

---

## 1. OpenAI as default, sensitive prompts stay local

**Goal:** Use OpenAI for most requests; if the prompt contains words like “internal” or “confidential”, route to local (Ollama) so that text never leaves your network.

**Behavior:** Sensitivity rule first → any configured keyword in the prompt → local. Otherwise cost rule, then default → OpenAI.

**Add or set in `.env`:**

```env
DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
SENSITIVITY_KEYWORDS=internal,confidential,secret
```

Ensure Ollama is running and a model is pulled if you want those sensitive requests to succeed. Cost rule (length or USD) is optional; if you don’t set USD vars, the length rule applies (default: prefer local when prompt ≤ 1000 chars).

---

## 2. Local only (Ollama)

**Goal:** All chat goes to Ollama; no cloud provider.

**Behavior:** Set default to local. You can leave sensitivity/cost rules as-is; they also route to local when they match. Unmatched requests still go to local because of default.

**Add or set in `.env`:**

```env
DEFAULT_PROVIDER=local
OLLAMA_BASE_URL=http://localhost:11434
```

No `OPENAI_API_KEY` needed. Start Ollama and pull a model (e.g. `ollama pull llama2`). In Docker Compose, use `OLLAMA_BASE_URL=http://ollama:11434` (set in `docker-compose.yml` for the app service).

---

## 3. USD cost threshold (prefer local when estimated cost is low)

**Goal:** Prefer local when the estimated OpenAI input cost is below a cap (e.g. $0.10); otherwise send to OpenAI.

**Behavior:** When both `COST_MAX_USD_FOR_LOCAL` and `OPENAI_INPUT_USD_PER_1K_TOKENS` are set, the cost rule uses USD. If estimated cost ≤ threshold → local; else → default (typically OpenAI).

**Add or set in `.env`:**

```env
DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
COST_MAX_USD_FOR_LOCAL=0.10
OPENAI_INPUT_USD_PER_1K_TOKENS=0.0015
COST_CHARS_PER_TOKEN=4
```

To **never** prefer local by cost (always use default unless sensitivity matches), set:

```env
COST_MAX_USD_FOR_LOCAL=0
OPENAI_INPUT_USD_PER_1K_TOKENS=0.0015
```

---

## 4. Audit disabled

**Goal:** Run without persisting audit events (e.g. no Postgres, or DB only for other uses).

**Behavior:** The app still routes and calls providers; it just does not write audit events. `GET /v1/audit/{request_id}` will return 404 for new requests.

**Add or set in `.env`:**

```env
AUDIT_ENABLED=false
```

You can leave `DATABASE_URL` set or unset; if it’s set but `AUDIT_ENABLED=false`, the app will not write audit events.

---

## Combining scenarios

You can combine:

- **OpenAI default + sensitive local + USD cost:** Use scenario 1 and 3 together (sensitivity keywords + USD vars).
- **Local only + audit disabled:** Use scenario 2 and 4; no Postgres or OpenAI needed.

After editing `.env`, restart the app (e.g. `docker compose up -d app` or restart uvicorn). Check effective policy with `curl -s http://localhost:8000/v1/routes`.
