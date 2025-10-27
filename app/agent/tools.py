from __future__ import annotations

from typing import Any

from app.clients.transaction_api import TransactionApiClient
from app.services.conversation_service import ConversationState
from app.services.transaction_service import TransactionService
from app.models.transaction import TransactionStatus
from app.utils.phone import normalize_phone_number


class AgentTools:
    def __init__(self, client: TransactionApiClient, transaction_service: TransactionService) -> None:
        self.client = client
        self.transaction_service = transaction_service

    async def format_phone_number_tool(self, phone: str) -> str | None:
        return normalize_phone_number(phone)

    async def validate_transaction_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.client.validate_transaction(payload)

    async def execute_transaction_tool(
        self,
        conversation_state: ConversationState,
        conversation_id,
    ) -> dict[str, Any]:
        payload = {
            "recipient_phone": conversation_state.phone_number,
            "amount": conversation_state.amount,
            "currency": conversation_state.currency,
        }
        response = await self.client.execute_transaction(payload)
        transaction_id = response.get("transaction_id")
        status_value = response.get("status", "pending")
        status = TransactionStatus(status_value) if status_value in TransactionStatus._value2member_map_ else TransactionStatus.PENDING
        await self.transaction_service.create_transaction(
            conversation_id=conversation_id,
            transaction_id=transaction_id,
            recipient_phone=conversation_state.phone_number or "",
            amount=conversation_state.amount or 0,
            status=status,
            currency=conversation_state.currency,
            error_message=response.get("error"),
        )
        return response

    async def get_transaction_status_tool(self, transaction_id: str) -> dict[str, Any]:
        return await self.client.get_transaction_status(transaction_id)
