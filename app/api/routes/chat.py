"""POST /v1/chat: validate body, call orchestrator, return response."""

from fastapi import APIRouter, Response

from app.api.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_orchestrator import handle_chat_request

router = APIRouter()


@router.post("/v1/chat", response_model=ChatResponse)
def post_chat(body: ChatRequest, response: Response) -> ChatResponse:
    """Chat endpoint: decision → provider → audit → response."""
    result = handle_chat_request(body)
    response.headers["X-Request-Id"] = result.request_id
    return result
