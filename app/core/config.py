"""Environment-driven application settings."""

import os
from dataclasses import dataclass


def get_database_url() -> str | None:
    """Return DATABASE_URL from environment; used for audit persistence and migrations."""
    return os.getenv("DATABASE_URL")


def get_audit_enabled() -> bool:
    """Return whether audit persistence is enabled (default True when DATABASE_URL is set)."""
    raw = os.getenv("AUDIT_ENABLED", "").lower()
    if raw in ("0", "false", "no"):
        return False
    if raw in ("1", "true", "yes"):
        return True
    return get_database_url() is not None


@dataclass(frozen=True)
class PolicyConfig:
    """Policy thresholds and keywords for decision engine (all from env)."""

    sensitivity_keywords: tuple[str, ...]
    cost_max_prompt_length_for_local: int
    default_provider: str  # "local" | "openai"


def get_policy_config() -> PolicyConfig:
    """
    Load policy config from environment.
    Defaults: empty sensitivity keywords, 1000 max prompt length for local, default_provider=openai.
    """
    raw_kw = os.getenv("SENSITIVITY_KEYWORDS", "")
    sensitivity_keywords = tuple(
        s.strip().lower() for s in raw_kw.split(",") if s.strip()
    )
    raw_len = os.getenv("COST_MAX_PROMPT_LENGTH_FOR_LOCAL", "1000")
    try:
        cost_max_prompt_length_for_local = max(0, int(raw_len))
    except ValueError:
        cost_max_prompt_length_for_local = 1000
    default_provider = (os.getenv("DEFAULT_PROVIDER", "openai") or "openai").strip().lower()
    if default_provider not in ("local", "openai"):
        default_provider = "openai"
    return PolicyConfig(
        sensitivity_keywords=sensitivity_keywords,
        cost_max_prompt_length_for_local=cost_max_prompt_length_for_local,
        default_provider=default_provider,
    )
