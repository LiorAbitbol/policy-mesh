"""Shared fixtures. Default policy file so POLICY_FILE is set for integration tests."""

import pytest

DEFAULT_POLICY_JSON = """{
  "sensitivity": { "keywords": [] },
  "cost": {
    "max_prompt_length_for_local": 1000,
    "max_usd_for_local": null,
    "input_usd_per_1m_tokens": null,
    "chars_per_token": 4,
    "default_provider": "public"
  }
}"""


@pytest.fixture(autouse=True)
def policy_file_env(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """
    Set POLICY_FILE to a valid temp policy file so endpoints that need policy can run.
    Tests that need custom policy can overwrite POLICY_FILE with their own temp file.
    """
    policy_path = tmp_path / "policies.json"
    policy_path.write_text(DEFAULT_POLICY_JSON, encoding="utf-8")
    monkeypatch.setenv("POLICY_FILE", str(policy_path))
    return policy_path
