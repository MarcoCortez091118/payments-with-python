from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.conversation_agent import ConversationAgent
from app.agent.tools import AgentTools
from app.api.deps import get_db_session
from app.clients.errors import CircuitBreakerOpen
from app.clients.transaction_api import TransactionApiClient
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService, ConversationState
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1", tags=["chat"])

transaction_client = TransactionApiClient()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    conversation_service = ConversationService(session)
    transaction_service = TransactionService(session)
    tools = AgentTools(transaction_client, transaction_service)
    agent = ConversationAgent(tools)

    conversation = await conversation_service.get_or_create(request.user_id, request.conversation_id)
    state = ConversationState.from_dict(conversation.context)

    await conversation_service.record_user_message(conversation, request.message)

    try:
        agent_response = await agent.handle(state, request.message, conversation.id)
    except CircuitBreakerOpen as exc:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    await conversation_service.record_agent_message(conversation, agent_response.text, agent_response.state)

    if agent_response.status == "completed":
        await conversation_service.complete_conversation(conversation)

    await session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=agent_response.text,
        context=agent_response.state.to_dict(),
        status=agent_response.status,
    )
