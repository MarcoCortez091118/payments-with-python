from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import JSON, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ConversationStatus(str, PyEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(length=64))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    context: Mapped[dict | None] = mapped_column(JSON, default=dict)
    messages: Mapped[list[dict]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
