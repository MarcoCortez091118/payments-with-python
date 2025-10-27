import pytest

from app.agent.conversation_agent import ConversationAgent
from app.services.conversation_service import ConversationState


class StubTools:
    async def format_phone_number_tool(self, phone: str):
        return phone

    async def validate_transaction_tool(self, payload):
        return {"status": "approved"}

    async def execute_transaction_tool(self, state, conversation_id):
        return {"transaction_id": "TXN-TEST", "status": "completed"}

    async def get_transaction_status_tool(self, transaction_id):
        return {"status": "completed"}


@pytest.mark.asyncio
async def test_conversation_flow_success():
    tools = StubTools()
    agent = ConversationAgent(tools)
    state = ConversationState()

    response1 = await agent.handle(state, "Hola, quiero enviar dinero", "conv-1")
    assert response1.status == "awaiting_phone"

    response2 = await agent.handle(state, "Al 3001234567", "conv-1")
    assert response2.status == "awaiting_amount"

    response3 = await agent.handle(state, "Enviar 50000 pesos", "conv-1")
    assert response3.status == "awaiting_confirmation"

    response4 = await agent.handle(state, "Si, confirmo", "conv-1")
    assert response4.status == "completed"
    assert "TXN-TEST" in response4.text
