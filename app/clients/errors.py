from __future__ import annotations


class CircuitBreakerOpen(Exception):
    """Raised when the circuit breaker is open."""


class TransactionApiError(Exception):
    """Raised when the transaction API returns an unexpected response."""
