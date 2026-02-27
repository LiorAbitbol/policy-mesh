"""Pydantic models for /v1/chat request and response. Aligned with providers.ChatResult and audit."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="user, assistant, or system")
    content: str = Field(..., description="message content")


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, description="chat messages")
    model: str | None = Field(None, description="optional model name (provider-specific default if omitted)")


class ChatResponse(BaseModel):
    """Success: content set. Failure: error set. provider and reason_codes always present."""

    request_id: str = Field(..., description="unique request id for audit traceability")
    provider: str = Field(..., description="local or openai")
    reason_codes: list[str] = Field(..., description="decision reason codes")
    content: str | None = Field(None, description="assistant reply (success)")
    error: str | None = Field(None, description="error message or failure category (failure)")
