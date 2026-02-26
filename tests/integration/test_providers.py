"""Integration tests for Ollama and OpenAI providers: mocked HTTP only (no real network)."""

from unittest.mock import MagicMock, patch

import httpx

from app.providers import ollama as ollama_module
from app.providers import openai as openai_module
from app.providers.base import (
    FAILURE_AUTH_ERROR,
    FAILURE_CLIENT_ERROR,
    FAILURE_SERVER_ERROR,
    FAILURE_TIMEOUT,
)


# ---- Ollama ----


def test_ollama_chat_success_returns_content() -> None:
    """Ollama: 200 with message.content → success and content."""
    mock_resp = httpx.Response(
        200,
        json={"message": {"role": "assistant", "content": "Hello from Ollama"}},
    )
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = ollama_module.chat(
        [{"role": "user", "content": "Hi"}],
        base_url="http://fake",
        timeout=10.0,
        client=mock_client,
    )

    assert result["success"] is True
    assert result["content"] == "Hello from Ollama"
    mock_client.post.assert_called_once()


def test_ollama_chat_4xx_returns_client_error() -> None:
    """Ollama: 4xx → failure_category client_error."""
    mock_resp = httpx.Response(404, text="not found")
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = ollama_module._request(
        mock_client,
        "http://fake/api/chat",
        {"model": "llama2", "messages": []},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_CLIENT_ERROR


def test_ollama_chat_5xx_returns_server_error() -> None:
    """Ollama: 5xx → failure_category server_error."""
    mock_resp = httpx.Response(502, text="Bad Gateway")
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = ollama_module._request(
        mock_client,
        "http://fake/api/chat",
        {"model": "llama2", "messages": []},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_SERVER_ERROR


def test_ollama_chat_timeout_returns_timeout_category() -> None:
    """Ollama: TimeoutException → failure_category timeout."""
    mock_client = MagicMock()
    mock_client.post.side_effect = httpx.TimeoutException("timed out")

    result = ollama_module._request(
        mock_client,
        "http://fake/api/chat",
        {"model": "llama2", "messages": []},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_TIMEOUT


# ---- OpenAI ----


def test_openai_chat_success_returns_content() -> None:
    """OpenAI: 200 with choices[0].message.content → success and content."""
    mock_resp = httpx.Response(
        200,
        json={
            "choices": [
                {"message": {"role": "assistant", "content": "Hello from OpenAI"}}
            ]
        },
    )
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = openai_module.chat(
        [{"role": "user", "content": "Hi"}],
        api_key="sk-fake",
        base_url="https://fake.openai.com",
        timeout=10.0,
        client=mock_client,
    )

    assert result["success"] is True
    assert result["content"] == "Hello from OpenAI"
    mock_client.post.assert_called_once()


def test_openai_chat_no_api_key_returns_auth_error() -> None:
    """OpenAI: no API key → failure_category auth_error (no HTTP call)."""
    with patch.object(openai_module, "get_openai_api_key", return_value=None):
        result = openai_module.chat(
            [{"role": "user", "content": "Hi"}],
            api_key=None,
            client=MagicMock(),
        )
    assert result["success"] is False
    assert result["failure_category"] == FAILURE_AUTH_ERROR


def test_openai_chat_401_returns_auth_error() -> None:
    """OpenAI: 401 → failure_category auth_error."""
    mock_resp = httpx.Response(401, text="Unauthorized")
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = openai_module._request(
        mock_client,
        "https://api.openai.com/v1/chat/completions",
        "sk-fake",
        {"model": "gpt-3.5-turbo", "messages": []},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_AUTH_ERROR


def test_openai_chat_5xx_returns_server_error() -> None:
    """OpenAI: 5xx → failure_category server_error."""
    mock_resp = httpx.Response(503, text="Service Unavailable")
    mock_client = MagicMock()
    mock_client.post.return_value = mock_resp

    result = openai_module._request(
        mock_client,
        "https://api.openai.com/v1/chat/completions",
        "sk-fake",
        {"model": "gpt-3.5-turbo", "messages": []},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_SERVER_ERROR


def test_openai_chat_timeout_returns_timeout_category() -> None:
    """OpenAI: TimeoutException → failure_category timeout."""
    mock_client = MagicMock()
    mock_client.post.side_effect = httpx.TimeoutException("timed out")

    result = openai_module._request(
        mock_client,
        "https://api.openai.com/v1/chat/completions",
        "sk-fake",
        {"model": "gpt-3.5-turbo", "messages": []},
        10.0,
    )

    assert result["success"] is False
    assert result["failure_category"] == FAILURE_TIMEOUT


def test_both_providers_share_interface() -> None:
    """Both providers return ChatResult with success and either content or failure_category."""
    ollama_ok = ollama_module._request(
        MagicMock(post=MagicMock(return_value=httpx.Response(
            200, json={"message": {"content": "x"}}
        ))),
        "http://f/api/chat",
        {"model": "x", "messages": []},
        1.0,
    )
    openai_ok = openai_module._request(
        MagicMock(post=MagicMock(return_value=httpx.Response(
            200, json={"choices": [{"message": {"content": "y"}}]}
        ))),
        "https://f/v1/chat/completions",
        "key",
        {"model": "x", "messages": []},
        1.0,
    )
    assert "success" in ollama_ok and "success" in openai_ok
    assert ollama_ok["success"] is True and openai_ok["success"] is True
    assert ollama_ok["content"] == "x" and openai_ok["content"] == "y"
