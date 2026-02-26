"""Decision orchestration: sensitivity → cost → default; returns provider + reason_codes."""

from typing import TypedDict

from app.core.config import PolicyConfig, get_policy_config
from app.decision.policies import cost_prefer_local, sensitivity_match
from app.decision.reason_codes import (
    COST_PREFER_LOCAL,
    DEFAULT_OPENAI,
    SENSITIVE_KEYWORD_MATCH,
)


class DecisionResult(TypedDict):
    provider: str  # "local" | "openai"
    reason_codes: list[str]


def decide(
    prompt_text: str = "",
    prompt_length: int = 0,
    config: PolicyConfig | None = None,
) -> DecisionResult:
    """
    Deterministic routing: sensitivity first, then cost, then default.
    Same input + config → same output. Returns provider and reason_codes on every path.
    """
    if config is None:
        config = get_policy_config()

    # 1. Sensitivity: any configured keyword in prompt → local
    if sensitivity_match(prompt_text, config.sensitivity_keywords):
        return {"provider": "local", "reason_codes": [SENSITIVE_KEYWORD_MATCH]}

    # 2. Cost: prompt length under threshold → prefer local
    if cost_prefer_local(prompt_length, config.cost_max_prompt_length_for_local):
        return {"provider": "local", "reason_codes": [COST_PREFER_LOCAL]}

    # 3. Default: openai (or config.default_provider)
    return {"provider": config.default_provider, "reason_codes": [DEFAULT_OPENAI]}
