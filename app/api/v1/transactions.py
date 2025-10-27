from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.transaction import TransactionRead
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1", tags=["transactions"])


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> TransactionRead:
    service = TransactionService(session)
    transaction = await service.get_by_transaction_id(transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionRead.model_validate(transaction)
