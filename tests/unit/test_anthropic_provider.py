"""Unit tests for Anthropic provider adapter: mocked httpx only."""

from unittest.mock import MagicMock, patch

import httpx

from app.providers import anthropic as anthropic_module
from app.providers.base import (
    FAILURE_AUTH_ERROR,
    FAILURE_CLIENT_ERROR,
    FAILURE_TIMEOUT,
)


def test_anthropic_chat_success_returns_content() -> None:
    """Anthropic: 200 with content[].text → success and content."""
    mock_resp = httpx.Response(
        200,
        json={
            "content": [{"type": "text", "text": "Hello from Claude"}],
            "model": "claude-3-5-sonnet-20241022",
        },
    )
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = anthropic_module.chat(
        [{"role": "user", "content": "Hi"}],
        api_key="sk-fake",
        base_url="https://api.anthropic.com",
        timeout=10.0,
        client=mock_client,
    )

    assert result["success"] is True
    assert result["content"] == "Hello from Claude"
    mock_client.post.assert_called_once()
    call_kw = mock_client.post.call_args[1]
    assert call_kw["headers"].get("x-api-key") == "sk-fake"
    assert call_kw["headers"].get("anthropic-version") == "2023-06-01"
    assert call_kw["json"]["model"] == "claude-3-5-sonnet-20241022"
    assert call_kw["json"]["messages"] == [{"role": "user", "content": "Hi"}]
    assert call_kw["json"]["max_tokens"] == 1024


def test_anthropic_chat_no_api_key_returns_auth_error() -> None:
    """Anthropic: no API key → failure_category auth_error (no HTTP call)."""
    with patch.object(anthropic_module, "get_public_llm_api_key", return_value=None):
        result = anthropic_module.chat(
            [{"role": "user", "content": "Hi"}],
            api_key=None,
            client=MagicMock(),
        )
    assert result["success"] is False
    assert result["failure_category"] == FAILURE_AUTH_ERROR


def test_anthropic_chat_401_returns_auth_error() -> None:
    """Anthropic: 401 → failure_category auth_error."""
    mock_resp = httpx.Response(401, text="Unauthorized")
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = anthropic_module._request(
        mock_client,
        "https://api.anthropic.com/v1/messages",
        "sk-fake",
        {"model": "claude-3-5-sonnet", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hi"}]},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_AUTH_ERROR


def test_anthropic_chat_timeout_returns_timeout_category() -> None:
    """Anthropic: TimeoutException → failure_category timeout."""
    mock_client = MagicMock()
    mock_client.post.side_effect = httpx.TimeoutException("timed out")

    result = anthropic_module._request(
        mock_client,
        "https://api.anthropic.com/v1/messages",
        "sk-fake",
        {"model": "claude-3-5-sonnet", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hi"}]},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_TIMEOUT


def test_anthropic_chat_4xx_returns_client_error() -> None:
    """Anthropic: 4xx → failure_category client_error."""
    mock_resp = httpx.Response(400, json={"error": {"message": "Bad request"}})
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = anthropic_module._request(
        mock_client,
        "https://api.anthropic.com/v1/messages",
        "sk-fake",
        {"model": "claude-3-5-sonnet", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hi"}]},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_CLIENT_ERROR


def test_anthropic_maps_system_messages_to_system_param() -> None:
    """Anthropic: system messages are sent as top-level system in request."""
    mock_resp = httpx.Response(
        200,
        json={"content": [{"type": "text", "text": "OK"}]},
    )
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    anthropic_module.chat(
        [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ],
        api_key="sk-fake",
        base_url="https://api.anthropic.com",
        client=mock_client,
    )

    call_json = mock_client.post.call_args[1]["json"]
    assert call_json["system"] == "You are helpful."
    assert call_json["messages"] == [{"role": "user", "content": "Hi"}]
