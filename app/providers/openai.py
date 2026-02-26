"""OpenAI API client: chat completions; API key, optional base URL, timeout from config."""

import httpx

from app.core.config import (
    get_openai_api_key,
    get_openai_base_url,
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

OPENAI_DEFAULT_BASE = "https://api.openai.com"


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
    Send chat completions to OpenAI (or OPENAI_BASE_URL). Uses config if not provided.
    messages: [{"role": "user"|"assistant"|"system", "content": "..."}]
    model: e.g. "gpt-4"; default "gpt-3.5-turbo" if omitted.
    """
    key = api_key or get_openai_api_key()
    if not key:
        return {"success": False, "failure_category": FAILURE_AUTH_ERROR, "message": "OPENAI_API_KEY not set"}
    url_base = (base_url or get_openai_base_url() or OPENAI_DEFAULT_BASE).rstrip("/")
    timeout_sec = timeout if timeout is not None else get_provider_timeout_seconds()
    model_name = model or "gpt-3.5-turbo"
    payload = {"model": model_name, "messages": messages}

    if client is not None:
        return _request(client, f"{url_base}/v1/chat/completions", key, payload, timeout_sec)

    with httpx.Client(timeout=timeout_sec) as c:
        return _request(c, f"{url_base}/v1/chat/completions", key, payload, timeout_sec)


def _request(
    client: httpx.Client,
    full_url: str,
    api_key: str,
    payload: dict,
    timeout_sec: float,
) -> ChatResult:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
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

    choices = data.get("choices") if isinstance(data, dict) else None
    if isinstance(choices, list) and len(choices) > 0:
        msg = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(msg, dict) and "content" in msg:
            return {"success": True, "content": str(msg["content"])}
    return {"success": False, "failure_category": FAILURE_UNKNOWN, "message": "Invalid response shape"}
