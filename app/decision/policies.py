"""Cost and sensitivity policy checks (config-driven; no hard-coded thresholds)."""


def sensitivity_match(prompt_text: str, sensitivity_keywords: tuple[str, ...]) -> bool:
    """
    True if prompt contains any of the configured sensitivity keywords (case-insensitive).
    Used to route to local when sensitive content is detected.
    """
    if not prompt_text or not sensitivity_keywords:
        return False
    lower = prompt_text.lower()
    return any(kw in lower for kw in sensitivity_keywords)


def cost_prefer_local(
    prompt_length: int,
    cost_max_prompt_length_for_local: int,
    cost_max_usd_for_local: float | None = None,
    openai_input_usd_per_1k_tokens: float | None = None,
    cost_chars_per_token: int = 4,
) -> bool:
    """
    Cost rule for preferring local provider.

    When both USD config values are set, use an approximate USD estimate:
    - tokens ~= prompt_length / cost_chars_per_token
    - cost_usd ~= (tokens / 1000) * openai_input_usd_per_1k_tokens
    Prefer local when cost_usd <= cost_max_usd_for_local.

    Otherwise, fall back to the legacy character-length threshold:
    True when prompt_length <= cost_max_prompt_length_for_local (with non-negative guard).
    """
    # Guard against negative inputs.
    if prompt_length < 0:
        prompt_length = 0

    # USD-mode: enabled only when both threshold and price are configured.
    if (
        cost_max_usd_for_local is not None
        and openai_input_usd_per_1k_tokens is not None
    ):
        if cost_chars_per_token <= 0:
            cost_chars_per_token = 4
        tokens_estimate = prompt_length / float(cost_chars_per_token)
        if tokens_estimate < 0:
            tokens_estimate = 0.0
        cost_usd = (tokens_estimate / 1000.0) * openai_input_usd_per_1k_tokens
        return cost_usd <= cost_max_usd_for_local

    # Legacy character-threshold mode.
    return cost_max_prompt_length_for_local >= 0 and prompt_length <= cost_max_prompt_length_for_local
