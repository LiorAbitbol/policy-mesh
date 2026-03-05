"""
Load policy from JSON file. POLICY_FILE must be set; file must exist and be valid.
Unknown top-level keys are ignored (extensibility). Uses stdlib json only.
"""

import json
import os

from app.core.config import PolicyConfig

POLICY_FILE_ENV = "POLICY_FILE"


class PolicyFileError(Exception):
    """Raised when POLICY_FILE is unset, file is missing, or JSON is invalid."""


def _get_policy_path() -> str:
    """Return POLICY_FILE path; raise PolicyFileError if unset or empty."""
    path = (os.getenv(POLICY_FILE_ENV) or "").strip()
    if not path:
        raise PolicyFileError(
            "POLICY_FILE is required but not set. Set POLICY_FILE to the path of a valid JSON policy file."
        )
    return path


def load_policy_config(path: str | None = None) -> PolicyConfig:
    """
    Load policy from JSON file. If path is None, use POLICY_FILE from env.
    Raises PolicyFileError if POLICY_FILE unset, file missing, or JSON invalid.
    Unknown top-level keys (e.g. capability) are ignored.
    """
    file_path = path if path is not None else _get_policy_path()
    file_path = os.path.expanduser(file_path)
    if not os.path.isfile(file_path):
        raise PolicyFileError(
            f"Policy file not found: {file_path}. POLICY_FILE must point to an existing JSON file."
        )

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise PolicyFileError(f"Policy file is not valid JSON: {file_path}. {e!s}") from e
    except OSError as e:
        raise PolicyFileError(f"Cannot read policy file: {file_path}. {e!s}") from e

    if not isinstance(data, dict):
        raise PolicyFileError(
            f"Policy file must be a JSON object; got {type(data).__name__}."
        )

    # Required: sensitivity object with keywords array
    sensitivity = data.get("sensitivity")
    if sensitivity is None:
        raise PolicyFileError("Policy file must contain a top-level 'sensitivity' object.")
    if not isinstance(sensitivity, dict):
        raise PolicyFileError(
            f"Policy 'sensitivity' must be an object; got {type(sensitivity).__name__}."
        )
    keywords_raw = sensitivity.get("keywords")
    if keywords_raw is None:
        raise PolicyFileError("Policy 'sensitivity' must contain 'keywords'.")
    if not isinstance(keywords_raw, list):
        raise PolicyFileError(
            f"Policy 'sensitivity.keywords' must be an array; got {type(keywords_raw).__name__}."
        )
    sensitivity_keywords = tuple(
        str(k).strip().lower() for k in keywords_raw if str(k).strip()
    )

    # Required: cost object; fields have defaults
    cost = data.get("cost")
    if cost is None:
        raise PolicyFileError("Policy file must contain a top-level 'cost' object.")
    if not isinstance(cost, dict):
        raise PolicyFileError(
            f"Policy 'cost' must be an object; got {type(cost).__name__}."
        )

    def _int(key: str, default: int, min_val: int = 0) -> int:
        v = cost.get(key)
        if v is None:
            return default
        try:
            n = int(v)
            return max(min_val, n) if key == "chars_per_token" else max(0, n)
        except (TypeError, ValueError):
            return default

    def _float_or_none(key: str) -> float | None:
        v = cost.get(key)
        if v is None:
            return None
        try:
            x = float(v)
            return x if x >= 0.0 else None
        except (TypeError, ValueError):
            return None

    def _positive_float_or_none(key: str) -> float | None:
        v = _float_or_none(key)
        return v if v is not None and v > 0.0 else None

    cost_max_prompt_length_for_local = _int("max_prompt_length_for_local", 1000)
    cost_max_usd_for_local = _float_or_none("max_usd_for_local")
    llm_input_usd_per_1m_tokens = _positive_float_or_none("input_usd_per_1m_tokens")
    cost_chars_per_token = _int("chars_per_token", 4, min_val=1)
    if cost_chars_per_token <= 0:
        cost_chars_per_token = 4

    default_provider_raw = (cost.get("default_provider") or "local")
    default_provider = str(default_provider_raw).strip().lower()
    if default_provider not in ("local", "public"):
        default_provider = "local"

    return PolicyConfig(
        sensitivity_keywords=sensitivity_keywords,
        cost_max_prompt_length_for_local=cost_max_prompt_length_for_local,
        default_provider=default_provider,
        cost_max_usd_for_local=cost_max_usd_for_local,
        llm_input_usd_per_1m_tokens=llm_input_usd_per_1m_tokens,
        cost_chars_per_token=cost_chars_per_token,
    )
