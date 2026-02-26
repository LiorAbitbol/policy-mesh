"""Integration tests for audit persistence (mocked repository; no real network)."""

from unittest.mock import patch

import pytest

from app.audit.context import AuditRequestContext
from app.audit.service import persist_audit_event


@patch("app.audit.service.save_audit_event")
def test_persist_audit_event_success_flow_writes_row_with_expected_fields(
    mock_save: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Request flow writes an audit row with request_id, decision, status, latency."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    monkeypatch.setenv("AUDIT_ENABLED", "true")
    ctx = AuditRequestContext(
        request_id="int-req-1",
        decision="provider=ollama,reason=default",
        status="success",
        latency_ms=25.0,
    )
    persist_audit_event(ctx)
    mock_save.assert_called_once()
    (event,) = mock_save.call_args[0]
    assert event.request_id == "int-req-1"
    assert event.decision == "provider=ollama,reason=default"
    assert event.status == "success"
    assert event.latency_ms == 25.0
    assert event.failure_category is None


@patch("app.audit.service.save_audit_event")
def test_persist_audit_event_failure_path_writes_row_with_failure_category(
    mock_save: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure path writes an audit row with failure_category."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@localhost/db")
    monkeypatch.setenv("AUDIT_ENABLED", "true")
    ctx = AuditRequestContext(
        request_id="int-req-fail",
        decision="provider=openai,reason=fallback",
        status="failure",
        latency_ms=500.0,
        failure_category="provider_error",
    )
    persist_audit_event(ctx)
    mock_save.assert_called_once()
    (event,) = mock_save.call_args[0]
    assert event.request_id == "int-req-fail"
    assert event.status == "failure"
    assert event.failure_category == "provider_error"


@patch("app.audit.service.save_audit_event")
def test_persist_audit_event_no_op_when_database_url_unset(
    mock_save: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When DATABASE_URL is not set, persist does not call save_audit_event."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("AUDIT_ENABLED", raising=False)
    ctx = AuditRequestContext(
        request_id="no-db",
        decision="provider=ollama",
        status="success",
        latency_ms=1.0,
    )
    persist_audit_event(ctx)
    mock_save.assert_not_called()
