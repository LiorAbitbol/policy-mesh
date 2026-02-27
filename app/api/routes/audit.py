"""GET /v1/audit/{request_id}: fetch one safe audit event view (no raw prompt)."""

from fastapi import APIRouter, HTTPException

from app.api.schemas.audit import AuditEventView
from app.audit.repository import get_audit_event_by_request_id
from app.core.config import get_audit_enabled, get_database_url

router = APIRouter()


@router.get("/v1/audit/{request_id}", response_model=AuditEventView)
def get_audit_event(request_id: str) -> AuditEventView:
    """
    Return a safe view of one audit event, or 404 when not found or audit is disabled/unavailable.
    """
    if not get_audit_enabled() or not get_database_url():
        raise HTTPException(status_code=404, detail="Audit event not found")
    try:
        event = get_audit_event_by_request_id(request_id)
    except Exception:
        # Treat database errors as unavailable for this endpoint per task requirements.
        raise HTTPException(status_code=404, detail="Audit event not found")
    if event is None:
        raise HTTPException(status_code=404, detail="Audit event not found")
    return AuditEventView(
        request_id=event.request_id,
        decision=event.decision,
        status=event.status,
        latency_ms=event.latency_ms,
        failure_category=event.failure_category,
        prompt_hash=event.prompt_hash,
        prompt_length=event.prompt_length,
        created_at=event.created_at,
    )
