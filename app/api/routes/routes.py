"""GET /v1/routes: effective policy view (rule order and thresholds; no secrets)."""

from fastapi import APIRouter

from app.api.schemas.routes import ROUTE_RULE_ORDER, RoutesResponse
from app.core.config import get_policy_config

router = APIRouter()


@router.get("/v1/routes", response_model=RoutesResponse)
def get_routes() -> RoutesResponse:
    """
    Return the current effective routing policy (read-only).
    Uses get_policy_config() as single source of truth. No API keys or secrets.
    """
    config = get_policy_config()
    return RoutesResponse(
        rule_order=list(ROUTE_RULE_ORDER),
        sensitivity_keyword_count=len(config.sensitivity_keywords),
        cost_max_prompt_length_for_local=config.cost_max_prompt_length_for_local,
        default_provider=config.default_provider,
    )
