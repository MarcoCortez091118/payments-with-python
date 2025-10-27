from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.main import app
from app.models.conversation import ConversationStatus
from app.api.deps import get_db_session


class StubTransactionClient:
    async def validate_transaction(self, payload):
        return {"status": "approved"}

    async def execute_transaction(self, payload):
        return {"transaction_id": "TXN-999", "status": "completed"}

    async def get_transaction_status(self, transaction_id):
        return {"status": "completed"}


@pytest.fixture
async def api_client(session, monkeypatch):
    stub_client = StubTransactionClient()
    monkeypatch.setattr("app.api.v1.chat.transaction_client", stub_client)

    async def override_session():
        yield session

    app.dependency_overrides[get_db_session] = override_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_endpoint_flow(api_client):
    payload = {"user_id": "user-1", "message": "Hola"}
    response = await api_client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    conversation_id = data["conversation_id"]
    assert data["status"] == "awaiting_phone"

    response = await api_client.post("/api/v1/chat", json={"user_id": "user-1", "message": "3001234567", "conversation_id": conversation_id})
    assert response.status_code == 200
    assert response.json()["status"] == "awaiting_amount"

    response = await api_client.post(
        "/api/v1/chat",
        json={"user_id": "user-1", "message": "Enviar 50000", "conversation_id": conversation_id},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "awaiting_confirmation"

    response = await api_client.post(
        "/api/v1/chat",
        json={"user_id": "user-1", "message": "Si confirmo", "conversation_id": conversation_id},
    )
    assert response.status_code == 200
    final_data = response.json()
    assert final_data["status"] == "completed"
    assert "TXN-999" in final_data["response"]

    history = await api_client.get(f"/api/v1/conversations/{conversation_id}")
    assert history.status_code == 200
    history_data = history.json()
    assert history_data["status"] == ConversationStatus.COMPLETED.value
    assert len(history_data["messages"]) >= 4

    transaction_response = await api_client.get("/api/v1/transactions/TXN-999")
    assert transaction_response.status_code == 200
