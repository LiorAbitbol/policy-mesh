# Configuration scenarios

This page gives copy-paste snippets for common setups. **Policy** (sensitivity, cost, default provider) is loaded from the JSON file at **POLICY_FILE** only; see [Policy file schema](POLICY_FILE_SCHEMA.md) and [policies.example.json](policies.example.json). The in-repo example lives in **docs/**; at runtime **POLICY_FILE** can be any path (e.g. `./policies.json` or `/etc/policy-mesh/policies.json`). Policy `default_provider` is **`local`** or **`public`** only; when `public`, the concrete provider (openai vs anthropic) comes from **PUBLIC_LLM_URL**. For behavior, see [Engine rules](ENGINE_RULES.md). Start from [.env.example](../.env.example) and set **POLICY_FILE** to your policy file path.

---

## 1. OpenAI as default, sensitive prompts stay local

**Goal:** Use OpenAI for most requests; if the prompt contains words like “internal” or “confidential”, route to local (Ollama) so that text never leaves your network.

**Behavior:** Sensitivity rule first → any configured keyword in the prompt → local. Otherwise cost rule, then default → OpenAI.

**In `.env`:** Set `POLICY_FILE` and `PUBLIC_LLM_API_KEY=sk-your-key-here`.

**In your policy file (e.g. policies.json):**

```json
{
  "sensitivity": { "keywords": ["internal", "confidential", "secret"] },
  "cost": {
    "max_prompt_length_for_local": 1000,
    "max_usd_for_local": null,
    "input_usd_per_1k_tokens": null,
    "chars_per_token": 4,
    "default_provider": "public"
  }
}
```

Ensure Ollama is running and a model is pulled if you want those sensitive requests to succeed. For Anthropic as default, set `PUBLIC_LLM_URL` to the Anthropic API base (e.g. `https://api.anthropic.com`) and use your Anthropic API key in `PUBLIC_LLM_API_KEY`.

---

## 2. Local only (Ollama)

**Goal:** All chat goes to Ollama; no cloud provider.

**Behavior:** Set default to local in the policy file. Unmatched requests still go to local because of default.

**In `.env`:** Set `POLICY_FILE` and `LOCAL_LLM_URL=http://localhost:11434` (or `http://ollama:11434` in Docker Compose).

**In your policy file:** Set `"default_provider": "local"` under `cost`. No `PUBLIC_LLM_API_KEY` needed. Start Ollama and pull a model (e.g. `ollama pull llama2`).

---

## 3. USD cost threshold (prefer local when estimated cost is low)

**Goal:** Prefer local when the estimated public LLM input cost is below a cap (e.g. $0.10); otherwise send to OpenAI.

**Behavior:** When both `max_usd_for_local` and `input_usd_per_1k_tokens` are set in the policy file, the cost rule uses USD. If estimated cost ≤ threshold → local; else → default (typically OpenAI).

**In `.env`:** Set `POLICY_FILE` and `PUBLIC_LLM_API_KEY=sk-your-key-here`.

**In your policy file:**

```json
{
  "sensitivity": { "keywords": [] },
  "cost": {
    "max_prompt_length_for_local": 1000,
    "max_usd_for_local": 0.10,
    "input_usd_per_1k_tokens": 0.0015,
    "chars_per_token": 4,
    "default_provider": "public"
  }
}
```

To **never** prefer local by cost, set `"max_usd_for_local": 0` (and keep `input_usd_per_1k_tokens` set).

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

- **OpenAI default + sensitive local + USD cost:** Use scenario 1 and 3 together in the same policy file (sensitivity keywords + cost USD fields).
- **Local only + audit disabled:** Use scenario 2 and 4; no Postgres or OpenAI needed.

After editing `.env` or the policy file, restart the app (e.g. `docker compose up -d app` or restart uvicorn). Check effective policy with `curl -s http://localhost:8000/v1/routes`.
