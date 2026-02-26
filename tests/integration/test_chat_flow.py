"""End-to-end /v1/chat orchestration tests with mocked decide, providers, and audit.

All tests use mocked providers (decide, ollama_provider, openai_provider, persist_audit_event);
no real network calls. Coverage: route behavior (local + openai success), fallback behavior
(provider failure → error + audit failure_category), audit write assertions, schema validation.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.audit.context import AuditRequestContext
from app.main import app


def test_chat_local_happy_path_returns_provider_reason_codes_content() -> None:
    """Route behavior (local): mocked decide → local, ollama.chat success → 200, provider, reason_codes, content; audit written with status=success."""
    with (
        patch("app.services.chat_orchestrator.decide") as mock_decide,
        patch("app.services.chat_orchestrator.ollama_provider") as mock_ollama,
        patch("app.services.chat_orchestrator.persist_audit_event") as mock_persist,
    ):
        mock_decide.return_value = {"provider": "local", "reason_codes": ["cost_prefer_local"]}
        mock_ollama.chat.return_value = {"success": True, "content": "Hello from Ollama"}

        client = TestClient(app)
        response = client.post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "local"
    assert data["reason_codes"] == ["cost_prefer_local"]
    assert data["content"] == "Hello from Ollama"
    assert data.get("error") is None
    mock_decide.assert_called_once()
    mock_ollama.chat.assert_called_once()
    mock_persist.assert_called_once()
    ctx: AuditRequestContext = mock_persist.call_args[0][0]
    assert ctx.request_id
    assert "provider=local" in ctx.decision
    assert "cost_prefer_local" in ctx.decision
    assert ctx.status == "success"
    assert ctx.latency_ms >= 0
    assert ctx.failure_category is None


def test_chat_openai_happy_path_returns_provider_reason_codes_content() -> None:
    """Route behavior (openai): mocked decide → openai, openai.chat success → 200, provider, reason_codes, content; audit written with status=success."""
    with (
        patch("app.services.chat_orchestrator.decide") as mock_decide,
        patch("app.services.chat_orchestrator.openai_provider") as mock_openai,
        patch("app.services.chat_orchestrator.persist_audit_event") as mock_persist,
    ):
        mock_decide.return_value = {"provider": "openai", "reason_codes": ["default_openai"]}
        mock_openai.chat.return_value = {"success": True, "content": "Hello from OpenAI"}

        client = TestClient(app)
        response = client.post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openai"
    assert data["reason_codes"] == ["default_openai"]
    assert data["content"] == "Hello from OpenAI"
    assert data.get("error") is None
    mock_decide.assert_called_once()
    mock_openai.chat.assert_called_once()
    mock_persist.assert_called_once()
    ctx: AuditRequestContext = mock_persist.call_args[0][0]
    assert ctx.request_id
    assert "provider=openai" in ctx.decision
    assert "default_openai" in ctx.decision
    assert ctx.status == "success"
    assert ctx.latency_ms >= 0
    assert ctx.failure_category is None


def test_chat_provider_failure_returns_error_and_audit_with_failure_category() -> None:
    """Fallback behavior: provider failure → 200 with error; audit write with status=failure and failure_category."""
    with (
        patch("app.services.chat_orchestrator.decide") as mock_decide,
        patch("app.services.chat_orchestrator.openai_provider") as mock_openai,
        patch("app.services.chat_orchestrator.persist_audit_event") as mock_persist,
    ):
        mock_decide.return_value = {"provider": "openai", "reason_codes": ["default_openai"]}
        mock_openai.chat.return_value = {
            "success": False,
            "failure_category": "timeout",
            "message": "Request timed out",
        }

        client = TestClient(app)
        response = client.post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openai"
    assert data["reason_codes"] == ["default_openai"]
    assert data.get("content") is None
    assert data["error"]  # "Request timed out" or failure_category
    mock_persist.assert_called_once()
    ctx: AuditRequestContext = mock_persist.call_args[0][0]
    assert ctx.status == "failure"
    assert ctx.failure_category == "timeout"


def test_chat_validates_request_schema() -> None:
    """Empty messages or invalid body → 422."""
    client = TestClient(app)
    r = client.post("/v1/chat", json={"messages": []})
    assert r.status_code == 422
    r2 = client.post("/v1/chat", json={})
    assert r2.status_code == 422
