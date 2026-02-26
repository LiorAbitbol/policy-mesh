"""Unit tests for audit record construction from request context (no DB)."""

import pytest

from app.audit.context import AuditRequestContext
from app.audit.service import build_audit_event


def test_build_audit_event_from_context_success() -> None:
    """AuditEvent built from context has request_id, decision, status, latency."""
    ctx = AuditRequestContext(
        request_id="req-123",
        decision="provider=ollama,reason=default",
        status="success",
        latency_ms=42.5,
    )
    event = build_audit_event(ctx)
    assert event.request_id == "req-123"
    assert event.decision == "provider=ollama,reason=default"
    assert event.status == "success"
    assert event.latency_ms == 42.5
    assert event.failure_category is None
    assert event.prompt_hash is None
    assert event.prompt_length is None
    assert event.prompt_flags is None
    assert event.created_at is not None


def test_build_audit_event_from_context_failure_with_category() -> None:
    """Failure path: event includes failure_category."""
    ctx = AuditRequestContext(
        request_id="req-fail-1",
        decision="provider=openai,reason=fallback",
        status="failure",
        latency_ms=100.0,
        failure_category="provider_timeout",
    )
    event = build_audit_event(ctx)
    assert event.request_id == "req-fail-1"
    assert event.status == "failure"
    assert event.failure_category == "provider_timeout"


def test_build_audit_event_includes_safe_prompt_metadata() -> None:
    """Event includes prompt_hash, prompt_length, prompt_flags only (no raw prompt)."""
    ctx = AuditRequestContext(
        request_id="req-meta",
        decision="provider=ollama",
        status="success",
        latency_ms=10.0,
        prompt_hash="sha256:abc123",
        prompt_length=500,
        prompt_flags="sensitive=0",
    )
    event = build_audit_event(ctx)
    assert event.prompt_hash == "sha256:abc123"
    assert event.prompt_length == 500
    assert event.prompt_flags == "sensitive=0"
    d = event.to_dict()
    assert "request_id" in d
    assert "decision" in d
    assert "status" in d
    assert "latency_ms" in d
    assert "prompt_hash" in d
    assert "prompt_length" in d
    assert "prompt_flags" in d
    assert "prompt" not in d and "raw_prompt" not in d
