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
    prompt_length: int, cost_max_prompt_length_for_local: int
) -> bool:
    """
    True when prompt length is at or under the configured threshold.
    Used to prefer local provider for shorter (cheaper) requests.
    """
    return cost_max_prompt_length_for_local >= 0 and prompt_length <= cost_max_prompt_length_for_local
