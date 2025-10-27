from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.transaction import Transaction, TransactionStatus


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.logger = get_logger(self.__class__.__name__)

    async def create_transaction(
        self,
        conversation_id: uuid.UUID,
        transaction_id: str,
        recipient_phone: str,
        amount: float,
        status: TransactionStatus,
        currency: str = "COP",
        error_message: str | None = None,
    ) -> Transaction:
        transaction = Transaction(
            conversation_id=conversation_id,
            transaction_id=transaction_id,
            recipient_phone=recipient_phone,
            amount=amount,
            status=status,
            currency=currency,
            error_message=error_message,
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_by_transaction_id(self, transaction_id: str) -> Transaction | None:
        stmt = select(Transaction).where(Transaction.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_conversation(self, conversation_id: uuid.UUID) -> list[Transaction]:
        stmt = select(Transaction).where(Transaction.conversation_id == conversation_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        transaction: Transaction,
        status: TransactionStatus,
        error_message: str | None = None,
    ) -> Transaction:
        transaction.status = status
        transaction.error_message = error_message
        transaction.updated_at = datetime.utcnow()
        await self.session.flush()
        return transaction
