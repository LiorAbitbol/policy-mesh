"""Integration tests for GET /v1/audit/{request_id}: safe audit view, 404 when disabled/unavailable. No real DB."""

from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.audit.models import AuditEvent
from app.main import app


def test_get_audit_event_returns_safe_fields_when_found() -> None:
    client = TestClient(app)
    event = AuditEvent(
        request_id="req-123",
        decision="provider=local,reason_codes=cost_prefer_local",
        status="success",
        latency_ms=12.3,
        failure_category=None,
        prompt_hash="abc",
        prompt_length=5,
        prompt_flags=None,
        created_at=datetime.now(timezone.utc),
    )
    with (
        patch("app.api.routes.audit.get_audit_enabled", return_value=True),
        patch("app.api.routes.audit.get_database_url", return_value="postgresql+psycopg://u:p@h/db"),
        patch("app.api.routes.audit.get_audit_event_by_request_id", return_value=event),
    ):
        resp = client.get("/v1/audit/req-123")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {
        "request_id",
        "decision",
        "status",
        "latency_ms",
        "failure_category",
        "prompt_hash",
        "prompt_length",
        "created_at",
    }
    assert body["request_id"] == "req-123"
    assert body["decision"] == "provider=local,reason_codes=cost_prefer_local"
    assert body["status"] == "success"
    assert body["failure_category"] is None
    assert "prompt" not in body and "raw_prompt" not in body


def test_get_audit_event_returns_404_when_not_found() -> None:
    client = TestClient(app)
    with (
        patch("app.api.routes.audit.get_audit_enabled", return_value=True),
        patch("app.api.routes.audit.get_database_url", return_value="postgresql+psycopg://u:p@h/db"),
        patch("app.api.routes.audit.get_audit_event_by_request_id", return_value=None),
    ):
        resp = client.get("/v1/audit/missing")
    assert resp.status_code == 404


def test_get_audit_event_returns_404_when_audit_disabled_and_does_not_hit_repo() -> None:
    client = TestClient(app)
    with (
        patch("app.api.routes.audit.get_audit_enabled", return_value=False),
        patch("app.api.routes.audit.get_database_url", return_value=None),
        patch("app.api.routes.audit.get_audit_event_by_request_id") as mock_repo,
    ):
        resp = client.get("/v1/audit/anything")
    assert resp.status_code == 404
    mock_repo.assert_not_called()
