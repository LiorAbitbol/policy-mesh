"""Audit write orchestration: build event from request context and persist."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.audit.context import AuditRequestContext
from app.audit.models import AuditEvent
from app.audit.repository import save_audit_event
from app.core.config import get_audit_enabled, get_database_url

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def build_audit_event(ctx: AuditRequestContext) -> AuditEvent:
    """Construct an AuditEvent from request context (no DB). Used by unit tests and by persist."""
    return AuditEvent(
        request_id=ctx.request_id,
        decision=ctx.decision,
        status=ctx.status,
        latency_ms=ctx.latency_ms,
        failure_category=ctx.failure_category,
        prompt_hash=ctx.prompt_hash,
        prompt_length=ctx.prompt_length,
        prompt_flags=ctx.prompt_flags,
        created_at=datetime.now(timezone.utc),
    )


def persist_audit_event(ctx: AuditRequestContext, session: "Session | None" = None) -> None:
    """
    Build one audit event from context and persist to Postgres when enabled.
    When DATABASE_URL is not set or AUDIT_ENABLED=false, no-op.
    """
    if not get_audit_enabled() or not get_database_url():
        return
    event = build_audit_event(ctx)
    save_audit_event(event, session=session)
