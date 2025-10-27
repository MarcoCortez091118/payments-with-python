from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.clients.errors import CircuitBreakerOpen, TransactionApiError
from app.core.config import get_settings
from app.core.logging import get_logger


@dataclass
class CircuitState:
    failure_count: int = 0
    state: str = "closed"
    opened_at: float | None = None
    half_open_trial: bool = False


class TransactionApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.transaction_api_base_url
        self.logger = get_logger(self.__class__.__name__)
        self.timeout = httpx.Timeout(connect=5.0, read=10.0)
        self._state = CircuitState()
        self._lock = asyncio.Lock()

    async def _check_circuit(self) -> None:
        async with self._lock:
            if self._state.state == "open":
                assert self._state.opened_at is not None
                elapsed = time.monotonic() - self._state.opened_at
                if elapsed < 30:
                    raise CircuitBreakerOpen("Circuit breaker is open")
                if elapsed >= 60 and not self._state.half_open_trial:
                    self._state.state = "half_open"
                    self._state.half_open_trial = True
                else:
                    raise CircuitBreakerOpen("Circuit breaker cooling down")
            elif self._state.state == "half_open" and self._state.half_open_trial:
                raise CircuitBreakerOpen("Half-open trial in progress")

    async def _record_success(self) -> None:
        async with self._lock:
            self._state = CircuitState()

    async def _record_failure(self) -> None:
        async with self._lock:
            self._state.failure_count += 1
            if self._state.state == "half_open":
                self._state.state = "open"
                self._state.opened_at = time.monotonic()
                self._state.half_open_trial = False
                return
            if self._state.failure_count >= 5:
                self._state.state = "open"
                self._state.opened_at = time.monotonic()
                self._state.half_open_trial = False

    async def _perform_request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        client = httpx.AsyncClient(timeout=self.timeout)
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=4),
                retry=retry_if_exception_type((httpx.HTTPError, TransactionApiError)),
                reraise=True,
            ):
                with attempt:
                    await self._check_circuit()
                    response = await client.request(method, url, **kwargs)
                    if response.status_code >= 500:
                        raise TransactionApiError(f"Server error {response.status_code}")
                    response.raise_for_status()
                    data = response.json()
                    await self._record_success()
                    return data
        except CircuitBreakerOpen:
            self.logger.warning("Circuit breaker open", path=path)
            raise
        except Exception as exc:  # noqa: BLE001
            self.logger.error("HTTP request failed", path=path, error=str(exc))
            await self._record_failure()
            raise
        finally:
            await client.aclose()
        raise TransactionApiError("Failed to perform request")

    async def validate_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._perform_request("POST", "/api/v1/transactions/validate", json=payload)

    async def execute_transaction(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._perform_request("POST", "/api/v1/transactions/execute", json=payload)

    async def get_transaction_status(self, transaction_id: str) -> dict[str, Any]:
        return await self._perform_request("GET", f"/api/v1/transactions/{transaction_id}")
