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
    default_provider: str  # "local" | "openai" | "anthropic"
    cost_max_usd_for_local: float | None
    llm_input_usd_per_1k_tokens: float | None
    cost_chars_per_token: int


def get_policy_config() -> PolicyConfig:
    """
    Load policy config from environment.
    Defaults:
    - sensitivity_keywords: empty tuple
    - cost_max_prompt_length_for_local: 1000
    - default_provider: "openai"
    - cost_max_usd_for_local: None (disabled)
    - llm_input_usd_per_1k_tokens: None (disabled)
    - cost_chars_per_token: 4
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
    if default_provider not in ("local", "openai", "anthropic"):
        default_provider = "openai"

    # Optional easy-mode USD cost gate (T-204). When either value is missing/invalid,
    # USD-mode is effectively disabled and the engine falls back to length-based cost.
    def _parse_positive_float(env_var: str) -> float | None:
        raw = os.getenv(env_var, "").strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            return None
        return value if value > 0.0 else None

    # COST_MAX_USD_FOR_LOCAL: allow 0 (meaning "never prefer local by USD"); otherwise must be positive.
    def _parse_cost_max_usd(env_var: str) -> float | None:
        raw = os.getenv(env_var, "").strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            return None
        return value if value >= 0.0 else None

    cost_max_usd_for_local = _parse_cost_max_usd("COST_MAX_USD_FOR_LOCAL")
    llm_input_usd_per_1k_tokens = _parse_positive_float(
        "LLM_INPUT_USD_PER_1K_TOKENS"
    )

    raw_chars_per_token = os.getenv("COST_CHARS_PER_TOKEN", "4").strip()
    try:
        cost_chars_per_token = int(raw_chars_per_token)
    except ValueError:
        cost_chars_per_token = 4
    if cost_chars_per_token <= 0:
        cost_chars_per_token = 4

    return PolicyConfig(
        sensitivity_keywords=sensitivity_keywords,
        cost_max_prompt_length_for_local=cost_max_prompt_length_for_local,
        default_provider=default_provider,
        cost_max_usd_for_local=cost_max_usd_for_local,
        llm_input_usd_per_1k_tokens=llm_input_usd_per_1k_tokens,
        cost_chars_per_token=cost_chars_per_token,
    )


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
