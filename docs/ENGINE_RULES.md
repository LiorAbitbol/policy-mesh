# Engine rules (routing policy)

The **decision engine** chooses which provider (local or cloud) handles each chat request. Rules are evaluated in a fixed order; the first match wins. All behavior is driven by environment variables—no hard-coded thresholds.

## Rule order

1. **Sensitivity** — If the prompt contains any configured keyword → route to **local**.
2. **Cost** — If the prompt is under the cost threshold (length or USD) → route to **local**.
3. **Default** — Otherwise → use the configured default provider (**openai** or **local**).

The response always includes `provider` and `reason_codes` so you can see why a request went to a given provider.

---

## 1. Sensitivity rule

**Purpose:** Keep prompts that mention sensitive topics on the local provider (e.g. “internal”, “confidential”) so they never leave your network.

| Variable | Type | Default | Effect |
|----------|------|---------|--------|
| `SENSITIVITY_KEYWORDS` | Comma-separated list | *(empty)* | Keywords that trigger local routing when found in the prompt (case-insensitive). |

**Behavior:**

- If `SENSITIVITY_KEYWORDS` is empty or unset, this rule is **skipped** (no keywords to match).
- The prompt is checked for **substring** matches; any keyword present → route to **local** with reason code `sensitive_keyword_match`.
- Matching is case-insensitive.

**Example:** `SENSITIVITY_KEYWORDS=internal,confidential,secret` → any prompt containing “internal”, “confidential”, or “secret” goes to local.

---

## 2. Cost rule

**Purpose:** Prefer the local provider when the estimated cost of sending the prompt to the cloud is below a threshold (so cheap/short prompts stay local).

The engine supports two modes. **Only one is active at a time:**

- **USD mode** — Used when both `COST_MAX_USD_FOR_LOCAL` and `OPENAI_INPUT_USD_PER_1K_TOKENS` are set. Compares an estimated OpenAI cost to the threshold.
- **Length mode** — Used when USD mode is not configured. Compares prompt length (characters) to a maximum length.

### USD mode (optional)

When both of these are set, the engine uses USD estimation and **ignores** the length threshold for the cost rule:

| Variable | Type | Default | Effect |
|----------|------|---------|--------|
| `COST_MAX_USD_FOR_LOCAL` | Float, ≥ 0 | *(not set)* | Prefer local when estimated prompt cost (USD) ≤ this value. Use `0` or `0.0` to never prefer local by cost (all prompts go to default unless sensitivity matches). |
| `OPENAI_INPUT_USD_PER_1K_TOKENS` | Float, > 0 | *(not set)* | Price in USD per 1k input tokens (e.g. `0.0015`). Used only when `COST_MAX_USD_FOR_LOCAL` is set. |
| `COST_CHARS_PER_TOKEN` | Integer, > 0 | `4` | Heuristic: tokens ≈ prompt length (chars) ÷ this value. Used for the USD estimate. |

**Formula:**
`tokens ≈ prompt_length / COST_CHARS_PER_TOKEN`
`cost_usd ≈ (tokens / 1000) * OPENAI_INPUT_USD_PER_1K_TOKENS`
→ Prefer local when `cost_usd ≤ COST_MAX_USD_FOR_LOCAL`.

**Note:** This is an approximation. Actual tokenization and pricing may differ.

### Length mode (fallback)

When USD mode is **not** configured (either `COST_MAX_USD_FOR_LOCAL` or `OPENAI_INPUT_USD_PER_1K_TOKENS` is missing/invalid), the cost rule uses character length only:

| Variable | Type | Default | Effect |
|----------|------|---------|--------|
| `COST_MAX_PROMPT_LENGTH_FOR_LOCAL` | Integer, ≥ 0 | `1000` | Prefer local when prompt length (characters) ≤ this value. |

**Behavior:**

- If USD mode is active, this variable is **not** used for the cost rule (it may still appear in `/v1/routes` for reference).
- If USD mode is off, the engine prefers local when `prompt_length ≤ COST_MAX_PROMPT_LENGTH_FOR_LOCAL`.

**Reason code:** When the cost rule matches (either mode), the response uses `cost_prefer_local`.

---

## 3. Default provider

**Purpose:** When neither sensitivity nor cost rule applies, send the request to the configured default provider.

| Variable | Type | Default | Effect |
|----------|------|---------|--------|
| `DEFAULT_PROVIDER` | `openai` \| `local` | `openai` | Provider used when no rule above matches. Invalid values fall back to `openai`. |

**Reason code:** The response uses `default_openai` when the default provider is chosen (even if the provider is `local`—the code name is historical).

---

## Summary table (routing only)

| Variable | Used by | When it applies |
|----------|---------|------------------|
| `SENSITIVITY_KEYWORDS` | Sensitivity rule | Always (empty = rule skipped). |
| `COST_MAX_USD_FOR_LOCAL` | Cost rule (USD mode) | Only when also set with `OPENAI_INPUT_USD_PER_1K_TOKENS`. |
| `OPENAI_INPUT_USD_PER_1K_TOKENS` | Cost rule (USD mode) | Only when also set with `COST_MAX_USD_FOR_LOCAL`. |
| `COST_CHARS_PER_TOKEN` | Cost rule (USD mode) | Only when USD mode is active. |
| `COST_MAX_PROMPT_LENGTH_FOR_LOCAL` | Cost rule (length mode) | Only when USD mode is **not** active. |
| `DEFAULT_PROVIDER` | Default step | When no sensitivity or cost match. |

---

## Viewing the effective policy

At runtime, the app exposes a read-only view of the effective routing policy (no secrets):

```bash
curl -s http://localhost:8000/v1/routes
```

The response includes which mode is active (USD vs length), thresholds, default provider, and sensitivity keyword count (keywords themselves are not exposed).
