"""Integration tests for GET /v1/routes: effective policy view. No real network."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


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
    assert body["default_provider"] in ("local", "openai")


def test_get_routes_reflects_env_sensitivity_keywords(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENSITIVITY_KEYWORDS", "foo, bar, baz")
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["sensitivity_keyword_count"] == 3


def test_get_routes_reflects_env_cost_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COST_MAX_PROMPT_LENGTH_FOR_LOCAL", "500")
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["cost_max_prompt_length_for_local"] == 500


def test_get_routes_reflects_env_default_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEFAULT_PROVIDER", "local")
    client = TestClient(app)
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    assert resp.json()["default_provider"] == "local"


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
    }
