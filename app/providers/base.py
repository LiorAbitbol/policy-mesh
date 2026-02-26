"""Shared provider interface: chat method, return shape, failure categories."""

from typing import Protocol, TypedDict


class ChatSuccess(TypedDict):
    success: bool  # True
    content: str


class ChatFailure(TypedDict):
    success: bool  # False
    failure_category: str
    message: str | None


ChatResult = ChatSuccess | ChatFailure

# Failure categories for audit and callers (consistent across providers).
FAILURE_TIMEOUT = "timeout"
FAILURE_CLIENT_ERROR = "client_error"  # 4xx
FAILURE_SERVER_ERROR = "server_error"  # 5xx
FAILURE_AUTH_ERROR = "auth_error"      # 401
FAILURE_UNKNOWN = "unknown"


class BaseChatProvider(Protocol):
    """Interface implemented by Ollama and OpenAI adapters."""

    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> ChatResult:
        """
        Send chat messages and return content or failure.
        messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
        model: optional model name (provider-specific default if omitted).
        """
        ...
