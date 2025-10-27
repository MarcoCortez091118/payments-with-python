from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.transaction import TransactionStatus


class TransactionRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    transaction_id: str
    recipient_phone: str
    amount: float
    currency: str
    status: TransactionStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True
