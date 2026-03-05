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
    """Policy thresholds and keywords for decision engine (from POLICY_FILE only)."""

    sensitivity_keywords: tuple[str, ...]
    cost_max_prompt_length_for_local: int
    default_provider: str  # "local" | "public" (resolved to openai|anthropic in decision engine)
    cost_max_usd_for_local: float | None
    llm_input_usd_per_1m_tokens: float | None
    cost_chars_per_token: int


def get_policy_config() -> PolicyConfig:
    """
    Load policy config from the file specified by POLICY_FILE.
    POLICY_FILE must be set and the file must exist and be valid JSON; otherwise raises PolicyFileError.
    Env is not a policy source.
    """
    from app.core.policy_file import load_policy_config

    return load_policy_config()


def get_local_llm_url() -> str:
    """Local LLM base URL (default http://localhost:11434). From env LOCAL_LLM_URL."""
    url = (os.getenv("LOCAL_LLM_URL") or "http://localhost:11434").strip()
    return url.rstrip("/")


def get_local_llm_api_key() -> str | None:
    """Optional API key for local LLM (e.g. Ollama with auth). From env LOCAL_LLM_API_KEY."""
    return os.getenv("LOCAL_LLM_API_KEY") or None


def get_public_llm_url() -> str:
    """Public/cloud LLM base URL (default https://api.openai.com). From env PUBLIC_LLM_URL."""
    url = (os.getenv("PUBLIC_LLM_URL") or "https://api.openai.com").strip()
    return url.rstrip("/")


def get_public_llm_api_key() -> str | None:
    """Public LLM API key from env. No default; no secrets in code."""
    return os.getenv("PUBLIC_LLM_API_KEY") or None


def get_public_provider_from_url() -> str:
    """
    Infer public provider from PUBLIC_LLM_URL (e.g. host contains anthropic → anthropic).
    Returns "anthropic" if URL host contains "anthropic", else "openai".
    """
    url = get_public_llm_url().lower()
    if "anthropic" in url:
        return "anthropic"
    return "openai"


def get_provider_timeout_seconds() -> float:
    """Provider HTTP timeout in seconds (default 60.0). From env PROVIDER_TIMEOUT_SECONDS."""
    raw = os.getenv("PROVIDER_TIMEOUT_SECONDS", "60").strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 60.0
