"""
/v1/chat orchestration: request_id → decide → provider chat → latency → audit → metrics stub → response.
"""

import hashlib
import time
import uuid

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.audit.context import AuditRequestContext
from app.audit.service import persist_audit_event
from app.decision.engine import decide
from app.providers import ollama as ollama_provider
from app.providers import openai as openai_provider
from app.services.metrics_stub import record_chat_request


def _prompt_from_request(body: ChatRequest) -> tuple[str, int]:
    """Extract prompt text and length for decision (last user message content)."""
    prompt_parts: list[str] = []
    for m in body.messages:
        if m.role == "user":
            prompt_parts.append(m.content)
    prompt_text = prompt_parts[-1] if prompt_parts else ""
    return prompt_text, len(prompt_text)


def _decision_string(provider: str, reason_codes: list[str]) -> str:
    """Stable string for audit: provider=X,reason_codes=A,B."""
    codes = ",".join(reason_codes) if reason_codes else ""
    return f"provider={provider},reason_codes={codes}"


def _messages_for_provider(body: ChatRequest) -> list[dict[str, str]]:
    """Convert request messages to provider format."""
    return [{"role": m.role, "content": m.content} for m in body.messages]


def handle_chat_request(body: ChatRequest) -> ChatResponse:
    """
    Run full orchestration: decide → provider → audit → metrics stub → response.
    Returns ChatResponse with provider, reason_codes, and content (success) or error (failure).
    """
    request_id = str(uuid.uuid4())
    prompt_text, prompt_length = _prompt_from_request(body)
    decision = decide(prompt_text=prompt_text, prompt_length=prompt_length)
    provider_key = decision["provider"]
    reason_codes = decision["reason_codes"]
    messages = _messages_for_provider(body)
    model = body.model

    start = time.perf_counter()
    if provider_key == "local":
        result = ollama_provider.chat(messages, model=model)
    else:
        result = openai_provider.chat(messages, model=model)
    latency_ms = (time.perf_counter() - start) * 1000.0

    decision_str = _decision_string(provider_key, reason_codes)
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest() if prompt_text else None
    prompt_flags = None  # placeholder for future flags

    if result.get("success"):
        status = "success"
        failure_category = None
    else:
        status = "failure"
        failure_category = result.get("failure_category") or "unknown"

    ctx = AuditRequestContext(
        request_id=request_id,
        decision=decision_str,
        status=status,
        latency_ms=latency_ms,
        failure_category=failure_category,
        prompt_hash=prompt_hash,
        prompt_length=prompt_length if prompt_text else None,
        prompt_flags=prompt_flags,
    )
    persist_audit_event(ctx)
    record_chat_request(request_id, provider_key, reason_codes, status, latency_ms)

    if result.get("success"):
        return ChatResponse(
            provider=provider_key,
            reason_codes=reason_codes,
            content=result.get("content", ""),
            error=None,
        )
    return ChatResponse(
        provider=provider_key,
        reason_codes=reason_codes,
        content=None,
        error=result.get("message") or result.get("failure_category", "unknown"),
    )
