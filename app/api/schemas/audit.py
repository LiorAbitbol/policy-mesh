"""Pydantic model for safe audit event view (no raw prompt)."""

from datetime import datetime

from pydantic import BaseModel, Field


class AuditEventView(BaseModel):
    request_id: str = Field(..., description="request id for traceability")
    decision: str = Field(..., description="decision string (provider + reason codes)")
    status: str = Field(..., description="success or failure")
    latency_ms: float = Field(..., description="end-to-end provider latency in ms")
    failure_category: str | None = Field(None, description="normalized failure category")
    prompt_hash: str | None = Field(None, description="hash of prompt text (no raw prompt)")
    prompt_length: int | None = Field(None, description="prompt text length (no raw prompt)")
    created_at: datetime = Field(..., description="timestamp when audit event was created")
