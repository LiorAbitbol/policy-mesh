"""Prometheus metrics for chat requests: counters and latency histograms (low-cardinality labels)."""

from prometheus_client import Counter, Histogram, REGISTRY

CHAT_REQUESTS_TOTAL = Counter(
    "chat_requests_total",
    "Total chat requests",
    ["provider", "status"],
    registry=REGISTRY,
)
CHAT_REQUEST_LATENCY_SECONDS = Histogram(
    "chat_request_latency_seconds",
    "Chat request latency in seconds",
    ["provider"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
    registry=REGISTRY,
)


def record_chat_request(
    request_id: str,
    provider: str,
    reason_codes: list[str],
    status: str,
    latency_ms: float,
) -> None:
    """Increment chat_requests_total and observe latency for Prometheus."""
    CHAT_REQUESTS_TOTAL.labels(provider=provider, status=status).inc()
    CHAT_REQUEST_LATENCY_SECONDS.labels(provider=provider).observe(latency_ms / 1000.0)
