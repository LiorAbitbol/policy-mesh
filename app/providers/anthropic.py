"""Anthropic Messages API client via httpx; same contract as OpenAI/Ollama."""

import httpx

from app.core.config import (
    get_public_llm_api_key,
    get_public_llm_url,
    get_provider_timeout_seconds,
)
from app.providers.base import (
    FAILURE_AUTH_ERROR,
    FAILURE_CLIENT_ERROR,
    FAILURE_SERVER_ERROR,
    FAILURE_TIMEOUT,
    FAILURE_UNKNOWN,
    ChatResult,
)

ANTHROPIC_DEFAULT_BASE = "https://api.anthropic.com"
ANTHROPIC_API_VERSION = "2023-06-01"
DEFAULT_MAX_TOKENS = 1024


def _anthropic_base_url() -> str:
    """Use PUBLIC_LLM_URL when it indicates Anthropic, else Anthropic default."""
    url = get_public_llm_url()
    if "anthropic" in url.lower():
        return url
    return ANTHROPIC_DEFAULT_BASE


def _to_anthropic_messages(messages: list[dict[str, str]]) -> tuple[str | None, list[dict]]:
    """
    Map our messages (user/assistant/system) to Anthropic format.
    Returns (system_text, messages_list). Anthropic messages only have user/assistant.
    """
    system_parts: list[str] = []
    anthropic_messages: list[dict] = []
    for m in messages:
        role = (m.get("role") or "user").lower()
        content = (m.get("content") or "").strip()
        if role == "system":
            system_parts.append(content)
        elif role in ("user", "assistant"):
            anthropic_messages.append({"role": role, "content": content})
    system_text = "\n".join(system_parts).strip() if system_parts else None
    return system_text, anthropic_messages


def chat(
    messages: list[dict[str, str]],
    model: str | None = None,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
    client: httpx.Client | None = None,
) -> ChatResult:
    """
    Call Anthropic Messages API. Uses PUBLIC_LLM_API_KEY and PUBLIC_LLM_URL (or Anthropic default).
    messages: [{"role": "user"|"assistant"|"system", "content": "..."}]
    model: e.g. "claude-3-5-sonnet-20241022"; default "claude-3-5-sonnet-20241022" if omitted.
    """
    key = api_key or get_public_llm_api_key()
    if not key:
        return {"success": False, "failure_category": FAILURE_AUTH_ERROR, "message": "PUBLIC_LLM_API_KEY not set"}
    url_base = (base_url or _anthropic_base_url()).rstrip("/")
    timeout_sec = timeout if timeout is not None else get_provider_timeout_seconds()
    model_name = model or "claude-3-5-sonnet-20241022"
    system_text, anthropic_messages = _to_anthropic_messages(messages)
    if not anthropic_messages:
        return {"success": False, "failure_category": FAILURE_CLIENT_ERROR, "message": "At least one user or assistant message required"}

    payload: dict = {
        "model": model_name,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "messages": anthropic_messages,
    }
    if system_text:
        payload["system"] = system_text

    full_url = f"{url_base}/v1/messages"
    if client is not None:
        return _request(client, full_url, key, payload, timeout_sec)
    with httpx.Client(timeout=timeout_sec) as c:
        return _request(c, full_url, key, payload, timeout_sec)


def _request(
    client: httpx.Client,
    full_url: str,
    api_key: str,
    payload: dict,
    timeout_sec: float,
) -> ChatResult:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "Content-Type": "application/json",
    }
    try:
        resp = client.post(full_url, json=payload, headers=headers, timeout=timeout_sec)
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

    content_blocks = data.get("content") if isinstance(data, dict) else None
    if isinstance(content_blocks, list):
        text_parts = []
        for block in content_blocks:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(str(block.get("text", "")))
        if text_parts:
            return {"success": True, "content": "\n".join(text_parts)}
    return {"success": False, "failure_category": FAILURE_UNKNOWN, "message": "Invalid response shape"}
