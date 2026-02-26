"""Ollama API client: POST /api/chat; configurable base URL and timeout."""

import httpx

from app.core.config import get_ollama_base_url, get_provider_timeout_seconds
from app.providers.base import (
    FAILURE_AUTH_ERROR,
    FAILURE_CLIENT_ERROR,
    FAILURE_SERVER_ERROR,
    FAILURE_TIMEOUT,
    FAILURE_UNKNOWN,
    ChatResult,
)


def chat(
    messages: list[dict[str, str]],
    model: str | None = None,
    *,
    base_url: str | None = None,
    timeout: float | None = None,
    client: httpx.Client | None = None,
) -> ChatResult:
    """
    Send chat to Ollama /api/chat. Uses config if base_url/timeout/client not provided.
    messages: [{"role": "user"|"assistant"|"system", "content": "..."}]
    model: e.g. "llama2"; default "llama2" if omitted.
    """
    url = base_url or get_ollama_base_url()
    timeout_sec = timeout if timeout is not None else get_provider_timeout_seconds()
    model_name = model or "llama2"
    payload = {"model": model_name, "messages": messages, "stream": False}

    if client is not None:
        return _request(client, f"{url}/api/chat", payload, timeout_sec)

    with httpx.Client(timeout=timeout_sec) as c:
        return _request(c, f"{url}/api/chat", payload, timeout_sec)


def _request(
    client: httpx.Client, full_url: str, payload: dict, timeout_sec: float
) -> ChatResult:
    try:
        resp = client.post(full_url, json=payload, timeout=timeout_sec)
    except httpx.TimeoutException:
        return {"success": False, "failure_category": FAILURE_TIMEOUT, "message": "Request timed out"}
    except httpx.RequestError as e:
        return {"success": False, "failure_category": FAILURE_UNKNOWN, "message": str(e)}

    if resp.status_code == 401:
        return {"success": False, "failure_category": FAILURE_AUTH_ERROR, "message": "Unauthorized"}
    if 400 <= resp.status_code < 500:
        return {"success": False, "failure_category": FAILURE_CLIENT_ERROR, "message": resp.text or None}
    if resp.status_code >= 500:
        return {"success": False, "failure_category": FAILURE_SERVER_ERROR, "message": resp.text or None}

    if resp.status_code != 200:
        return {"success": False, "failure_category": FAILURE_UNKNOWN, "message": resp.text or None}

    try:
        data = resp.json()
    except Exception as e:
        return {"success": False, "failure_category": FAILURE_UNKNOWN, "message": str(e)}

    message = data.get("message") if isinstance(data, dict) else None
    if isinstance(message, dict) and "content" in message:
        return {"success": True, "content": str(message["content"])}
    return {"success": False, "failure_category": FAILURE_UNKNOWN, "message": "Invalid response shape"}
