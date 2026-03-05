"""Integration tests for GET /v1/routes: effective policy view. No real network."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import DEFAULT_POLICY_JSON


def test_get_routes_returns_200_and_expected_keys() -> None:
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    body = resp.json()
    assert "rule_order" in body
    assert "sensitivity_keyword_count" in body
    assert "cost_max_prompt_length_for_local" in body
    assert "default_provider" in body
    assert body["rule_order"] == ["sensitivity", "cost", "default"]
    assert body["sensitivity_keyword_count"] >= 0
    assert body["cost_max_prompt_length_for_local"] >= 0
    assert body["default_provider"] in ("local", "public")


def test_get_routes_reflects_policy_file_sensitivity_keywords(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = json.loads(DEFAULT_POLICY_JSON)
    policy["sensitivity"]["keywords"] = ["foo", "bar", "baz"]
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    monkeypatch.setenv("POLICY_FILE", str(path))
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["sensitivity_keyword_count"] == 3


def test_get_routes_reflects_policy_file_cost_threshold(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = json.loads(DEFAULT_POLICY_JSON)
    policy["cost"]["max_prompt_length_for_local"] = 500
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    monkeypatch.setenv("POLICY_FILE", str(path))
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["cost_max_prompt_length_for_local"] == 500


def test_get_routes_reflects_policy_file_default_provider_local(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = json.loads(DEFAULT_POLICY_JSON)
    policy["cost"]["default_provider"] = "local"
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    monkeypatch.setenv("POLICY_FILE", str(path))
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["default_provider"] == "local"


def test_get_routes_reflects_policy_file_default_provider_public(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = json.loads(DEFAULT_POLICY_JSON)
    policy["cost"]["default_provider"] = "public"
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    monkeypatch.setenv("POLICY_FILE", str(path))
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["default_provider"] == "public"


def test_get_routes_available_public_provider_reflects_public_llm_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PUBLIC_LLM_URL", "https://api.anthropic.com")
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["available_public_provider"] == "anthropic"


def test_get_routes_does_not_expose_secrets() -> None:
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {
        "rule_order",
        "sensitivity_keyword_count",
        "cost_max_prompt_length_for_local",
        "default_provider",
        "usd_cost_mode_active",
        "cost_max_usd_for_local",
        "llm_input_usd_per_1m_tokens",
        "cost_chars_per_token",
        "available_public_provider",
    }


def test_get_routes_policy_file_unset_returns_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """When POLICY_FILE is unset, endpoint that needs policy returns 500."""
    monkeypatch.setenv("POLICY_FILE", "")
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 500


def test_get_routes_policy_file_invalid_json_returns_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When POLICY_FILE points to invalid JSON, endpoint returns 500."""
    path = tmp_path / "bad.json"
    path.write_text("not valid json {", encoding="utf-8")
    monkeypatch.setenv("POLICY_FILE", str(path))
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 500


def test_get_routes_policy_file_missing_returns_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When POLICY_FILE points to a nonexistent file, endpoint returns 500."""
    missing_path = tmp_path / "nonexistent.json"
    assert not missing_path.exists()
    monkeypatch.setenv("POLICY_FILE", str(missing_path))
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 500


def test_decision_engine_uses_file_policy(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """When POLICY_FILE points to valid file, decision engine uses file-derived policy (sensitivity)."""
    policy = json.loads(DEFAULT_POLICY_JSON)
    policy["sensitivity"]["keywords"] = ["secret"]
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    monkeypatch.setenv("POLICY_FILE", str(path))
    from app.core.config import get_policy_config
    from app.decision.engine import decide

    config = get_policy_config()
    assert config.sensitivity_keywords == ("secret",)
    result = decide(prompt_text="This is secret data", prompt_length=10, config=config)
    assert result["provider"] == "local"
    assert "sensitive_keyword_match" in result["reason_codes"]
