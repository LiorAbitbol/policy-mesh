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
    default_provider: str = Field(
        ...,
        description="Provider used when no sensitivity or cost rule applies (local or openai).",
    )
