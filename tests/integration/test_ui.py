"""Integration tests for minimal UI (T-203): GET / and GET /ui serve the static page."""

from fastapi.testclient import TestClient

from app.main import app


def test_get_root_returns_200_and_contains_ui_content() -> None:
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    body = resp.text
    assert "Policy Mesh" in body
    assert "Send" in body or "chat" in body.lower()
    assert "Load rules" in body or "rules" in body.lower()


def test_get_ui_path_returns_200_and_serves_same_page() -> None:
    client = TestClient(app)
    resp = client.get("/ui")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "Policy Mesh" in resp.text
