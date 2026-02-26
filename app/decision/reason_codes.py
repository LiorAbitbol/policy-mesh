"""Explicit reason code constants for routing decisions (stable contract)."""

# Sensitivity: prompt matched a configured keyword → route to local.
SENSITIVE_KEYWORD_MATCH = "sensitive_keyword_match"

# Cost: prompt under configured length threshold → prefer local.
COST_PREFER_LOCAL = "cost_prefer_local"

# Default: no sensitivity match and over cost threshold → route to openai.
DEFAULT_OPENAI = "default_openai"

# All known reason codes (for validation/documentation).
ALL_REASON_CODES = (
    SENSITIVE_KEYWORD_MATCH,
    COST_PREFER_LOCAL,
    DEFAULT_OPENAI,
)
