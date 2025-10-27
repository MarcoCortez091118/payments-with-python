from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.conversation import Conversation, ConversationStatus


@dataclass
class ConversationState:
    phone_number: str | None = None
    amount: float | None = None
    currency: str = "COP"
    stage: str = "greeting"

    def to_dict(self) -> dict:
        return {
            "phone_number": self.phone_number,
            "amount": self.amount,
            "currency": self.currency,
            "stage": self.stage,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "ConversationState":
        if not data:
            return cls()
        return cls(
            phone_number=data.get("phone_number"),
            amount=data.get("amount"),
            currency=data.get("currency", "COP"),
            stage=data.get("stage", "greeting"),
        )


def _append_message(conversation: Conversation, role: str, content: str) -> None:
    messages = list(conversation.messages or [])
    messages.append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    conversation.messages = messages


class ConversationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.logger = get_logger(self.__class__.__name__)

    async def get_or_create(self, user_id: str, conversation_id: uuid.UUID | None = None) -> Conversation:
        if conversation_id:
            conversation = await self.session.get(Conversation, conversation_id)
            if conversation:
                return conversation
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def record_user_message(self, conversation: Conversation, message: str) -> None:
        _append_message(conversation, "user", message)
        conversation.updated_at = datetime.utcnow()
        await self.session.flush()

    async def record_agent_message(self, conversation: Conversation, message: str, state: ConversationState) -> None:
        _append_message(conversation, "agent", message)
        conversation.context = state.to_dict()
        conversation.updated_at = datetime.utcnow()
        await self.session.flush()

    async def complete_conversation(self, conversation: Conversation) -> None:
        conversation.status = ConversationStatus.COMPLETED
        conversation.ended_at = datetime.utcnow()
        await self.session.flush()
