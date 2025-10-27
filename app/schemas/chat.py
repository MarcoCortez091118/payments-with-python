from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Identifier for the user initiating the chat")
    message: str = Field(..., description="User message to the agent")
    conversation_id: uuid.UUID | None = Field(default=None)


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    response: str
    context: dict[str, Any]
    status: str
