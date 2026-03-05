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
  - **default_provider** (string, optional): Provider when no rule matches: `local`, `openai`, or `anthropic`. Default: `openai`.

Unknown top-level keys (e.g. `capability`) are **ignored** and do not cause load failure (extensibility).

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
    "default_provider": "openai"
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
    "default_provider": "openai"
  }
}
```
