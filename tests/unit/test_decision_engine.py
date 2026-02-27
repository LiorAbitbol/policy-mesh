"""Unit tests for DecisionEngine: sensitive, cost, default branches and determinism."""

import pytest

from app.core.config import PolicyConfig
from app.decision.engine import decide
from app.decision.reason_codes import (
    COST_PREFER_LOCAL,
    DEFAULT_OPENAI,
    SENSITIVE_KEYWORD_MATCH,
)


def _config(
    keywords: tuple[str, ...] = (),
    max_length: int = 1000,
    default_provider: str = "openai",
    cost_max_usd_for_local: float | None = None,
    openai_input_usd_per_1k_tokens: float | None = None,
    cost_chars_per_token: int = 4,
) -> PolicyConfig:
    return PolicyConfig(
        sensitivity_keywords=keywords,
        cost_max_prompt_length_for_local=max_length,
        default_provider=default_provider,
        cost_max_usd_for_local=cost_max_usd_for_local,
        openai_input_usd_per_1k_tokens=openai_input_usd_per_1k_tokens,
        cost_chars_per_token=cost_chars_per_token,
    )


def test_sensitive_branch_keyword_in_prompt_returns_local() -> None:
    """Sensitivity: prompt contains configured keyword → provider=local, reason SENSITIVE_KEYWORD_MATCH."""
    config = _config(keywords=("internal", "confidential"))
    result = decide(prompt_text="This is internal data.", prompt_length=100, config=config)
    assert result["provider"] == "local"
    assert result["reason_codes"] == [SENSITIVE_KEYWORD_MATCH]


def test_sensitive_branch_case_insensitive() -> None:
    """Sensitivity match is case-insensitive."""
    config = _config(keywords=("secret",))
    result = decide(prompt_text="TOP SECRET report", prompt_length=50, config=config)
    assert result["provider"] == "local"
    assert result["reason_codes"] == [SENSITIVE_KEYWORD_MATCH]


def test_sensitive_branch_no_keyword_falls_through() -> None:
    """When no keyword matches, decision falls through to cost/default."""
    config = _config(keywords=("secret",), max_length=10)
    result = decide(prompt_text="Hello world", prompt_length=5, config=config)
    assert result["provider"] == "local"
    assert result["reason_codes"] == [COST_PREFER_LOCAL]


def test_cost_branch_under_threshold_returns_local() -> None:
    """Cost: prompt length under threshold → provider=local, reason COST_PREFER_LOCAL."""
    config = _config(keywords=(), max_length=500)
    result = decide(prompt_text="Short prompt", prompt_length=100, config=config)
    assert result["provider"] == "local"
    assert result["reason_codes"] == [COST_PREFER_LOCAL]


def test_cost_branch_over_threshold_returns_default() -> None:
    """Cost: prompt length over threshold → default provider (openai)."""
    config = _config(keywords=(), max_length=50)
    result = decide(prompt_text="x" * 100, prompt_length=100, config=config)
    assert result["provider"] == "openai"
    assert result["reason_codes"] == [DEFAULT_OPENAI]


def test_default_branch_returns_openai_and_reason_code() -> None:
    """Default: no sensitivity, over cost threshold → provider=openai, DEFAULT_OPENAI."""
    config = _config(keywords=(), max_length=10, default_provider="openai")
    result = decide(prompt_text="A long prompt that exceeds cost threshold", prompt_length=100, config=config)
    assert result["provider"] == "openai"
    assert result["reason_codes"] == [DEFAULT_OPENAI]


def test_default_provider_configurable() -> None:
    """Default provider can be set to local via config."""
    config = _config(keywords=(), max_length=10, default_provider="local")
    result = decide(prompt_text="Long prompt", prompt_length=100, config=config)
    assert result["provider"] == "local"
    assert result["reason_codes"] == [DEFAULT_OPENAI]


def test_determinism_same_input_same_decision() -> None:
    """Same prompt_text, prompt_length, and config → same decision every time."""
    config = _config(keywords=("x",), max_length=200)
    result1 = decide(prompt_text="foo bar", prompt_length=50, config=config)
    result2 = decide(prompt_text="foo bar", prompt_length=50, config=config)
    assert result1 == result2
    assert result1["provider"] == result2["provider"]
    assert result1["reason_codes"] == result2["reason_codes"]


def test_every_decision_has_provider_and_reason_codes() -> None:
    """Every path returns provider and reason_codes (contract)."""
    config = _config(keywords=("s",), max_length=5)
    for prompt_text, prompt_length in [("s", 1), ("", 2), ("long " * 20, 100)]:
        result = decide(prompt_text=prompt_text, prompt_length=prompt_length, config=config)
        assert "provider" in result
        assert "reason_codes" in result
        assert result["provider"] in ("local", "openai")
        assert isinstance(result["reason_codes"], list)
        assert len(result["reason_codes"]) >= 1


def test_cost_usd_mode_under_threshold_returns_local() -> None:
    """USD-mode: estimated cost under threshold → provider=local, COST_PREFER_LOCAL."""
    # USD-mode active when both cost_max_usd_for_local and openai_input_usd_per_1k_tokens are set.
    config = _config(
        keywords=(),
        max_length=10_000,
        cost_max_usd_for_local=0.05,
        openai_input_usd_per_1k_tokens=0.02,
        cost_chars_per_token=4,
    )
    # prompt_length=4_000 chars → tokens≈1_000 → cost≈(1000/1000)*0.02 = $0.02 < $0.05
    result = decide(prompt_text="x" * 4000, prompt_length=4000, config=config)
    assert result["provider"] == "local"
    assert result["reason_codes"] == [COST_PREFER_LOCAL]


def test_cost_usd_mode_over_threshold_returns_default_provider() -> None:
    """USD-mode: estimated cost over threshold → default provider with DEFAULT_OPENAI reason code."""
    config = _config(
        keywords=(),
        max_length=10_000,
        default_provider="openai",
        cost_max_usd_for_local=0.05,
        openai_input_usd_per_1k_tokens=0.02,
        cost_chars_per_token=4,
    )
    # prompt_length=12_000 chars → tokens≈3_000 → cost≈(3000/1000)*0.02 = $0.06 > $0.05
    result = decide(prompt_text="x" * 12_000, prompt_length=12_000, config=config)
    assert result["provider"] == "openai"
    assert result["reason_codes"] == [DEFAULT_OPENAI]


def test_cost_fallback_to_length_mode_when_usd_config_missing() -> None:
    """When USD config is unset, cost branch behaves like legacy character-threshold mode."""
    config = _config(keywords=(), max_length=50)
    # Under threshold → local
    under = decide(prompt_text="x" * 25, prompt_length=25, config=config)
    assert under["provider"] == "local"
    assert under["reason_codes"] == [COST_PREFER_LOCAL]
    # Over threshold → default (openai)
    over = decide(prompt_text="x" * 100, prompt_length=100, config=config)
    assert over["provider"] == "openai"
    assert over["reason_codes"] == [DEFAULT_OPENAI]
