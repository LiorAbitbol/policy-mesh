"""Reason code contract: stable constants used by DecisionEngine."""

from app.decision import reason_codes as rc


def test_all_reason_codes_defined_and_non_empty() -> None:
    """Every member of ALL_REASON_CODES is a non-empty string."""
    assert len(rc.ALL_REASON_CODES) >= 1
    for code in rc.ALL_REASON_CODES:
        assert isinstance(code, str)
        assert len(code) > 0


def test_sensitive_cost_default_codes_in_all() -> None:
    """SENSITIVE_KEYWORD_MATCH, COST_PREFER_LOCAL, DEFAULT_OPENAI are in ALL_REASON_CODES."""
    assert rc.SENSITIVE_KEYWORD_MATCH in rc.ALL_REASON_CODES
    assert rc.COST_PREFER_LOCAL in rc.ALL_REASON_CODES
    assert rc.DEFAULT_OPENAI in rc.ALL_REASON_CODES
