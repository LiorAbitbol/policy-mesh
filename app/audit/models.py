"""SQLAlchemy model for audit event storage."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for audit models."""

    pass


class AuditEvent(Base):
    """
    One row per chat request: request id, decision, status, latency,
    optional failure category and safe prompt metadata (no raw prompt).
    """

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    failure_category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_flags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"AuditEvent(id={self.id}, request_id={self.request_id!r}, status={self.status!r})"

    def to_dict(self) -> dict[str, Any]:
        """For tests and debugging: export as dict (no raw prompt)."""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "decision": self.decision,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "failure_category": self.failure_category,
            "prompt_hash": self.prompt_hash,
            "prompt_length": self.prompt_length,
            "prompt_flags": self.prompt_flags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
