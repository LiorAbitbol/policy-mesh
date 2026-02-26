"""No-op metrics hook for chat requests. T-106 will add real instrumentation."""

def record_chat_request(
    request_id: str,
    provider: str,
    reason_codes: list[str],
    status: str,
    latency_ms: float,
) -> None:
    """Record a chat request for metrics. No-op in T-105."""
    pass
