from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.conversation import ConversationStatus


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime


class ConversationContext(BaseModel):
    phone_number: str | None = None
    amount: float | None = None
    currency: str | None = "COP"
    state: str | None = None


class ConversationRead(BaseModel):
    id: uuid.UUID
    user_id: str
    started_at: datetime
    ended_at: datetime | None
    status: ConversationStatus
    context: ConversationContext | None
    messages: list[ConversationMessage]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True
