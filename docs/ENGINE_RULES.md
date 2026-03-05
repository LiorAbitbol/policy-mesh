# Engine rules (routing policy)

The **decision engine** chooses which provider (local or cloud) handles each chat request. Rules are evaluated in a fixed order; the first match wins. **Policy is loaded from a JSON file only:** **POLICY_FILE** must be set to the path of that file. If unset, or if the file is missing or invalid, the application errors. See [Policy file schema](POLICY_FILE_SCHEMA.md) and [policies.example.json](policies.example.json).

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

- **USD mode** — Used when both `cost.max_usd_for_local` and `cost.input_usd_per_1k_tokens` are set in the policy file. Compares an estimated public LLM cost to the threshold.
- **Length mode** — Used when USD mode is not configured. Compares prompt length (characters) to a maximum length.

### USD mode (optional)

When both of these are set in the policy file, the engine uses USD estimation and **ignores** the length threshold for the cost rule:

| Policy file (cost) | Type | Effect |
|--------------------|------|--------|
| `max_usd_for_local` | Number, ≥ 0, or null | Prefer local when estimated prompt cost (USD) ≤ this value. Use `0` or `null` to disable USD prefer-local. |
| `input_usd_per_1k_tokens` | Number, > 0, or null | Price in USD per 1k input tokens (e.g. `0.0015`). Required for USD mode. |
| `chars_per_token` | Integer, > 0 | Heuristic: tokens ≈ prompt length (chars) ÷ this value. Default: `4`. |

**Formula:**
`tokens ≈ prompt_length / chars_per_token`
`cost_usd ≈ (tokens / 1000) * input_usd_per_1k_tokens`
→ Prefer local when `cost_usd ≤ max_usd_for_local`.

**Note:** This is an approximation. Actual tokenization and pricing may differ.

### Length mode (fallback)

When USD mode is **not** configured (either `max_usd_for_local` or `input_usd_per_1k_tokens` is null/missing), the cost rule uses character length only:

| Policy file (cost) | Type | Effect |
|--------------------|------|--------|
| `max_prompt_length_for_local` | Integer, ≥ 0 | Prefer local when prompt length (characters) ≤ this value. Default: `1000`. |

**Behavior:**

- If USD mode is active, this field is **not** used for the cost rule (it may still appear in `/v1/routes` for reference).
- If USD mode is off, the engine prefers local when `prompt_length ≤ max_prompt_length_for_local`.

**Reason code:** When the cost rule matches (either mode), the response uses `cost_prefer_local`.

---

## 3. Default provider

**Purpose:** When neither sensitivity nor cost rule applies, send the request to the configured default provider.

| Policy file (cost) | Type | Effect |
|-------------------|------|--------|
| `default_provider` | `openai` \| `local` \| `anthropic` | Provider used when no rule above matches. Default: `openai`. |

**Reason code:** The response uses `default_openai` when the default provider is chosen (even if the provider is `local`—the code name is historical).

---

## Summary (policy file)

Policy is loaded from the JSON file at **POLICY_FILE**. Required top-level keys: **sensitivity** (with **keywords** array) and **cost** (with optional fields and defaults). See [Policy file schema](POLICY_FILE_SCHEMA.md).

---

## Viewing the effective policy

At runtime, the app exposes a read-only view of the effective routing policy (no secrets):

```bash
curl -s http://localhost:8000/v1/routes
```

The response includes which mode is active (USD vs length), thresholds, default provider, and sensitivity keyword count (keywords themselves are not exposed).
