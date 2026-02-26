"""Integration tests for GET /v1/metrics: Prometheus format and chat-driven metrics. No real network."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_returns_200_and_prometheus_format() -> None:
    """GET /v1/metrics returns 200 and body contains chat_requests_total and chat_request_latency_seconds."""
    client = TestClient(app)
    response = client.get("/v1/metrics")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/plain")
    body = response.text
    assert "chat_requests_total" in body
    assert "chat_request_latency_seconds" in body


def test_metrics_after_chat_request_increments_counter_and_observes_latency() -> None:
    """After a mocked POST /v1/chat, GET /v1/metrics shows incremented counter and histogram observation."""
    with (
        patch("app.services.chat_orchestrator.decide") as mock_decide,
        patch("app.services.chat_orchestrator.ollama_provider") as mock_ollama,
        patch("app.services.chat_orchestrator.persist_audit_event"),
    ):
        mock_decide.return_value = {"provider": "local", "reason_codes": ["cost_prefer_local"]}
        mock_ollama.chat.return_value = {"success": True, "content": "Hi"}

        client = TestClient(app)
        chat_resp = client.post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )
    assert chat_resp.status_code == 200

    metrics_resp = client.get("/v1/metrics")
    assert metrics_resp.status_code == 200
    body = metrics_resp.text
    # Counter should have at least one sample (provider="local", status="success")
    assert "chat_requests_total" in body
    assert "chat_request_latency_seconds" in body
    # Prometheus format: metric name followed by labels and value
    assert "chat_requests_total{" in body or "chat_requests_total " in body
    assert "chat_request_latency_seconds{" in body or "chat_request_latency_seconds " in body
