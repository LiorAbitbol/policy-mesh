# API usage

This guide describes how to call the Policy Mesh API from scripts, tools, or your application. For OpenAPI (Swagger) docs, use **http://localhost:8000/docs** when the app is running.

---

## Base URL and headers

- **Base URL:** `http://localhost:8000` (or your deployed host).
- **Content-Type:** `application/json` for request bodies.
- **Response:** JSON. On error (e.g. 500), the body may be plain text; check `response.ok` before parsing as JSON.

---

## POST /v1/chat

Send a chat request. The engine routes to a provider (local or OpenAI), calls it, persists an audit event, and returns the reply with routing metadata.

### Request body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | Yes | At least one message. Each object: `role` (`user`, `assistant`, or `system`) and `content` (string). |
| `model` | string | No | Optional model name; provider uses its default if omitted. |

**Example (minimal):**

```json
{
  "messages": [
    { "role": "user", "content": "Hello" }
  ]
}
```

**Example (with optional model):**

```json
{
  "messages": [
    { "role": "system", "content": "You are helpful." },
    { "role": "user", "content": "What is 2+2?" }
  ],
  "model": "gpt-4o-mini"
}
```

### Response (success)

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Unique ID for this request; use it to fetch the audit event from `/v1/audit/{request_id}`. |
| `provider` | string | `local` or `openai` — which provider handled the request. |
| `reason_codes` | array of strings | Why this provider was chosen (e.g. `sensitive_keyword_match`, `cost_prefer_local`, `default_openai`). |
| `content` | string | The assistant reply (present on success). |
| `error` | null | Omitted or null on success. |

**Example:**

```json
{
  "request_id": "abc-123-def",
  "provider": "openai",
  "reason_codes": ["default_openai"],
  "content": "Hello! How can I help you today?",
  "error": null
}
```

### Response (failure)

Same structure, but `content` is null and `error` contains a message or failure category. `provider` and `reason_codes` are still set (routing happened; the provider call failed).

**Example:**

```json
{
  "request_id": "abc-123-def",
  "provider": "openai",
  "reason_codes": ["default_openai"],
  "content": null,
  "error": "Provider request failed: ..."
}
```

The response also sets the **`X-Request-Id`** header to the same `request_id` for correlation.

### curl examples

**Success:**

```bash
curl -s -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

**With model:**

```bash
curl -s -X POST http://127.0.0.1:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Summarize in one sentence."}],"model":"gpt-4o-mini"}'
```

**Note:** The app does not stream; it waits for the full LLM response. Allow 10–60 seconds depending on provider and model.

### Minimal integration example (Python)

```python
import requests

def chat(text: str, base_url: str = "http://127.0.0.1:8000") -> dict:
    r = requests.post(
        f"{base_url}/v1/chat",
        json={"messages": [{"role": "user", "content": text}]},
        timeout=90,
    )
    r.raise_for_status()
    data = r.json()
    # Use data["request_id"] for audit lookup
    return data
```

---

## GET /v1/audit/{request_id}

Fetch the audit event for a given chat request. Returns only safe fields (no raw prompt).

### Path parameter

- **request_id** — The value from the `request_id` field (or `X-Request-Id` header) of the `/v1/chat` response.

### Response (200)

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Same as path. |
| `decision` | string | e.g. `provider=openai,reason_codes=default_openai`. |
| `status` | string | `success` or `failure`. |
| `latency_ms` | number | End-to-end provider latency in milliseconds. |
| `failure_category` | string or null | Normalized failure category when status is failure. |
| `prompt_hash` | string or null | Hash of the prompt (no raw prompt). |
| `prompt_length` | number or null | Prompt length in characters. |
| `created_at` | string (ISO datetime) | When the event was recorded. |

**Example:**

```bash
curl -s http://127.0.0.1:8000/v1/audit/abc-123-def
```

Returns 404 if the request_id is unknown or audit is disabled.

---

## GET /v1/routes

Returns the current effective routing policy (read-only). No secrets or keyword values are exposed.

### Response (200)

Includes: `rule_order`, `sensitivity_keyword_count`, `cost_max_prompt_length_for_local`, `usd_cost_mode_active`, `cost_max_usd_for_local`, `openai_input_usd_per_1k_tokens`, `cost_chars_per_token`, `default_provider`. See OpenAPI schema or [Engine rules](ENGINE_RULES.md) for meaning.

**Example:**

```bash
curl -s http://127.0.0.1:8000/v1/routes
```

---

## GET /v1/health

Liveness check. Returns `{"status":"ok"}`.

```bash
curl -s http://127.0.0.1:8000/v1/health
```

---

## GET /v1/metrics

Prometheus-format metrics (counters and histograms for chat requests). See [Metrics](METRICS.md) for details.

```bash
curl -s http://127.0.0.1:8000/v1/metrics
```
