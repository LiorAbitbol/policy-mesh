"""Pydantic model for GET /v1/routes: safe effective-policy view (no secrets)."""

from pydantic import BaseModel, Field

# Rule order matches app/decision/engine.py: sensitivity → cost → default.
ROUTE_RULE_ORDER = ("sensitivity", "cost", "default")


class RoutesResponse(BaseModel):
    """Effective routing policy (read-only). No API keys, env URLs, or secrets."""

    rule_order: list[str] = Field(
        ...,
        description="Order in which rules are evaluated: sensitivity, then cost, then default.",
    )
    sensitivity_keyword_count: int = Field(
        ...,
        description="Number of configured sensitivity keywords (keywords not exposed for privacy).",
        ge=0,
    )
    cost_max_prompt_length_for_local: int = Field(
        ...,
        description="Max prompt length (chars) below which cost rule prefers local.",
        ge=0,
    )
    usd_cost_mode_active: bool = Field(
        ...,
        description=(
            "Whether USD-based cost gate is active "
            "(True when both COST_MAX_USD_FOR_LOCAL and OPENAI_INPUT_USD_PER_1K_TOKENS are configured)."
        ),
    )
    cost_max_usd_for_local: float | None = Field(
        None,
        description="Maximum estimated OpenAI input cost in USD for which local is preferred (approximate).",
        ge=0,
    )
    openai_input_usd_per_1k_tokens: float | None = Field(
        None,
        description="Configured OpenAI input price in USD per 1K tokens (approximate; input-only).",
        ge=0,
    )
    cost_chars_per_token: int = Field(
        ...,
        description="Heuristic chars-per-token used for the USD estimate (tokens ≈ chars / cost_chars_per_token).",
        ge=1,
    )
    default_provider: str = Field(
        ...,
        description="Provider used when no sensitivity or cost rule applies (local or openai).",
    )
