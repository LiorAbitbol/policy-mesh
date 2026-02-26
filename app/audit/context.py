"""Request context for audit: no raw prompt, only safe metadata and outcome."""

from typing import Any


class AuditRequestContext:
    """
    Immutable context for building an AuditEvent.
    Includes decision (e.g. provider + reason codes), status, latency,
    optional failure category and safe prompt metadata only.
    """

    __slots__ = (
        "request_id",
        "decision",
        "status",
        "latency_ms",
        "failure_category",
        "prompt_hash",
        "prompt_length",
        "prompt_flags",
    )

    def __init__(
        self,
        request_id: str,
        decision: str,
        status: str,
        latency_ms: float,
        *,
        failure_category: str | None = None,
        prompt_hash: str | None = None,
        prompt_length: int | None = None,
        prompt_flags: str | None = None,
    ) -> None:
        self.request_id = request_id
        self.decision = decision
        self.status = status
        self.latency_ms = latency_ms
        self.failure_category = failure_category
        self.prompt_hash = prompt_hash
        self.prompt_length = prompt_length
        self.prompt_flags = prompt_flags

    def to_dict(self) -> dict[str, Any]:
        """For tests: dict representation (no raw prompt)."""
        return {
            "request_id": self.request_id,
            "decision": self.decision,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "failure_category": self.failure_category,
            "prompt_hash": self.prompt_hash,
            "prompt_length": self.prompt_length,
            "prompt_flags": self.prompt_flags,
        }
