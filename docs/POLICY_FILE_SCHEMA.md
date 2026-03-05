# Policy file schema

Policy is loaded from a JSON file. **POLICY_FILE** must be set to the path of that file. If unset, or if the file is missing or invalid JSON, the application errors (no fallback).

## Required

- **POLICY_FILE** (environment variable): Path to the JSON policy file. Must be set; file must exist and be valid.

## JSON structure

Top-level keys:

- **sensitivity** (object, required): Sensitivity rule configuration.
  - **keywords** (array of strings, required): Keywords that trigger local routing when found in the prompt (case-insensitive). May be empty `[]`.
- **cost** (object, required): Cost rule configuration.
  - **max_prompt_length_for_local** (integer, optional): Prefer local when prompt length (chars) ≤ this. Default: `1000`.
  - **max_usd_for_local** (number or null, optional): Prefer local when estimated cost (USD) ≤ this. Use `null` or omit to disable USD mode. Default: `null`.
  - **input_usd_per_1k_tokens** (number or null, optional): Price in USD per 1k input tokens for USD estimate. Required for USD mode when `max_usd_for_local` is set. Default: `null`.
  - **chars_per_token** (integer, optional): Heuristic for token estimate (tokens ≈ chars / this). Default: `4`.
  - **default_provider** (string, optional): Default when no rule matches: `local` or `public` only. Which public provider (openai vs anthropic) is derived from **PUBLIC_LLM_URL** at decision time, not from the policy file. Invalid or missing value defaults to `public`.

Unknown top-level keys (e.g. `capability`) are **ignored** and do not cause load failure (extensibility).

## Where the policy file lives

- **In-repo example:** An example policy file lives in **docs/** (e.g. `docs/policies.example.json`). Copy it and customize: `cp docs/policies.example.json ./policies.json`.
- **At runtime:** **POLICY_FILE** can be **any path** the operator chooses. The path is under operator control; there is no hardcoded location. Common choices:
  - Next to the app: `./policies.json` or `./config/policies.json`
  - System config: `/etc/policy-mesh/policies.json`

Set **POLICY_FILE** in your environment (or `.env`) to point to your JSON file.

## Example

See [policies.example.json](policies.example.json). Copy and customize:

```json
{
  "sensitivity": {
    "keywords": ["internal", "confidential", "secret"]
  },
  "cost": {
    "max_prompt_length_for_local": 1000,
    "max_usd_for_local": null,
    "input_usd_per_1k_tokens": null,
    "chars_per_token": 4,
    "default_provider": "public"
  }
}
```

USD mode example (prefer local when estimated cost ≤ 0.09):

```json
{
  "sensitivity": { "keywords": [] },
  "cost": {
    "max_prompt_length_for_local": 1000,
    "max_usd_for_local": 0.09,
    "input_usd_per_1k_tokens": 0.0015,
    "chars_per_token": 4,
    "default_provider": "public"
  }
}
```

**Migration:** If your policy file still has `default_provider: "openai"` or `"anthropic"`, replace with `"public"`. The concrete provider (openai vs anthropic) is determined by **PUBLIC_LLM_URL** at runtime.
