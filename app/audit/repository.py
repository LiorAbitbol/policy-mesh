"""Persistence adapter for audit events (Postgres backend, config-driven)."""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.audit.models import AuditEvent
from app.core.config import get_database_url


def _get_engine():
    """Create engine from DATABASE_URL; raises if URL is missing."""
    url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set; cannot create audit engine")
    return create_engine(url, pool_pre_ping=True)


def _session_factory():
    """Session factory bound to the configured engine (lazy)."""
    engine = _get_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


_session_maker: sessionmaker[Session] | None = None


def get_audit_session_factory() -> sessionmaker[Session]:
    """Return a session factory for audit persistence (singleton per process)."""
    global _session_maker
    if _session_maker is None:
        _session_maker = _session_factory()
    return _session_maker


def save_audit_event(event: AuditEvent, session: Session | None = None) -> None:
    """
    Persist one audit event. Uses provided session or a new one from config.
    Caller may pass a session for transactional tests.
    """
    if session is not None:
        session.add(event)
        session.commit()
        return
    factory = get_audit_session_factory()
    with factory() as s:
        s.add(event)
        s.commit()


def get_audit_event_by_request_id(
    request_id: str, session: Session | None = None
) -> AuditEvent | None:
    """Fetch one AuditEvent by request_id, or None when not found."""
    stmt = select(AuditEvent).where(AuditEvent.request_id == request_id).limit(1)
    if session is not None:
        return session.execute(stmt).scalar_one_or_none()
    factory = get_audit_session_factory()
    with factory() as s:
        return s.execute(stmt).scalar_one_or_none()
