"""Environment-driven application settings."""

import os


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
