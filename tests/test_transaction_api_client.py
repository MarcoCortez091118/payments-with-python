from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.clients.errors import CircuitBreakerOpen
from app.clients.transaction_api import TransactionApiClient


@pytest.mark.asyncio
async def test_retry_successful_request():
    client = TransactionApiClient(base_url="http://test")
    payload = {"amount": 10, "recipient_phone": "573001234567"}

    with respx.mock:
        route = respx.post("http://test/api/v1/transactions/validate").mock(
            side_effect=[
                Response(500, json={"detail": "error"}),
                Response(200, json={"status": "approved"}),
            ]
        )
        result = await client.validate_transaction(payload)

    assert route.call_count == 2
    assert result["status"] == "approved"


@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    client = TransactionApiClient(base_url="http://test")
    payload = {"amount": 10, "recipient_phone": "573001234567"}

    with respx.mock:
        respx.post("http://test/api/v1/transactions/validate").mock(
            return_value=Response(503, json={"detail": "error"})
        )
        for _ in range(5):
            with pytest.raises(Exception):
                await client.validate_transaction(payload)
        with pytest.raises(CircuitBreakerOpen):
            await client.validate_transaction(payload)
