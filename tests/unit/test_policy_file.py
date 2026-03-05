"""Unit tests for policy file loader: valid JSON, errors when unset/missing/invalid, unknown keys ignored."""

import json
import tempfile
from pathlib import Path

import pytest

from app.core.config import PolicyConfig
from app.core.policy_file import PolicyFileError, load_policy_config


def _valid_policy() -> dict:
    return {
        "sensitivity": {"keywords": ["internal", "confidential"]},
        "cost": {
            "max_prompt_length_for_local": 1000,
            "max_usd_for_local": None,
            "input_usd_per_1k_tokens": None,
            "chars_per_token": 4,
            "default_provider": "openai",
        },
    }


def test_load_policy_config_valid_json_produces_policy_config(tmp_path: Path) -> None:
    """Valid JSON with sensitivity and cost produces correct PolicyConfig."""
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(_valid_policy()), encoding="utf-8")
    config = load_policy_config(path=str(path))
    assert isinstance(config, PolicyConfig)
    assert config.sensitivity_keywords == ("internal", "confidential")
    assert config.cost_max_prompt_length_for_local == 1000
    assert config.default_provider == "openai"
    assert config.cost_max_usd_for_local is None
    assert config.llm_input_usd_per_1k_tokens is None
    assert config.cost_chars_per_token == 4


def test_load_policy_config_usd_mode(tmp_path: Path) -> None:
    """Policy with max_usd_for_local and input_usd_per_1k_tokens sets USD fields."""
    policy = _valid_policy()
    policy["cost"]["max_usd_for_local"] = 0.09
    policy["cost"]["input_usd_per_1k_tokens"] = 0.0015
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    config = load_policy_config(path=str(path))
    assert config.cost_max_usd_for_local == 0.09
    assert config.llm_input_usd_per_1k_tokens == 0.0015


def test_load_policy_config_default_provider_anthropic(tmp_path: Path) -> None:
    """Policy with default_provider anthropic is accepted."""
    policy = _valid_policy()
    policy["cost"]["default_provider"] = "anthropic"
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    config = load_policy_config(path=str(path))
    assert config.default_provider == "anthropic"


def test_load_policy_config_policy_file_unset_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """When POLICY_FILE is unset or empty, load_policy_config() raises PolicyFileError."""
    monkeypatch.setenv("POLICY_FILE", "")
    with pytest.raises(PolicyFileError) as exc_info:
        load_policy_config()
    assert "POLICY_FILE" in str(exc_info.value)
    assert "required" in str(exc_info.value).lower()


def test_load_policy_config_file_missing_raises() -> None:
    """When file does not exist, load_policy_config(path=...) raises PolicyFileError."""
    with tempfile.TemporaryDirectory() as d:
        missing = Path(d) / "nonexistent.json"
        with pytest.raises(PolicyFileError) as exc_info:
            load_policy_config(path=str(missing))
        assert "not found" in str(exc_info.value).lower() or "existing" in str(exc_info.value).lower()


def test_load_policy_config_invalid_json_raises(tmp_path: Path) -> None:
    """When file is not valid JSON, load_policy_config raises PolicyFileError."""
    path = tmp_path / "bad.json"
    path.write_text("not json {", encoding="utf-8")
    with pytest.raises(PolicyFileError) as exc_info:
        load_policy_config(path=str(path))
    assert "valid JSON" in str(exc_info.value) or "JSON" in str(exc_info.value)


def test_load_policy_config_missing_sensitivity_raises(tmp_path: Path) -> None:
    """When sensitivity is missing, loader raises PolicyFileError."""
    path = tmp_path / "policies.json"
    path.write_text(json.dumps({"cost": _valid_policy()["cost"]}), encoding="utf-8")
    with pytest.raises(PolicyFileError) as exc_info:
        load_policy_config(path=str(path))
    assert "sensitivity" in str(exc_info.value).lower()


def test_load_policy_config_missing_cost_raises(tmp_path: Path) -> None:
    """When cost is missing, loader raises PolicyFileError."""
    path = tmp_path / "policies.json"
    path.write_text(json.dumps({"sensitivity": _valid_policy()["sensitivity"]}), encoding="utf-8")
    with pytest.raises(PolicyFileError) as exc_info:
        load_policy_config(path=str(path))
    assert "cost" in str(exc_info.value).lower()


def test_load_policy_config_unknown_top_level_keys_ignored(tmp_path: Path) -> None:
    """Unknown top-level keys (e.g. capability) do not cause load failure."""
    policy = _valid_policy()
    policy["capability"] = {"some": "future"}
    policy["other"] = "ignored"
    path = tmp_path / "policies.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    config = load_policy_config(path=str(path))
    assert config.sensitivity_keywords == ("internal", "confidential")
    assert config.default_provider == "openai"
