"""GET /v1/metrics: Prometheus exposition format."""

from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import REGISTRY, generate_latest

# Ensure app metrics are registered (Counter, Histogram in telemetry)
from app.core import telemetry  # noqa: F401

CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"

router = APIRouter()


@router.get("/v1/metrics")
def get_metrics() -> Response:
    """Return metrics in Prometheus exposition format."""
    body = generate_latest(REGISTRY)
    return Response(content=body, media_type=CONTENT_TYPE)
