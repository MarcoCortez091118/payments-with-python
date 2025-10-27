from __future__ import annotations

import asyncio
import random
import string
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Mock Transactions API", version="0.1.0")

transactions_store: Dict[str, dict] = {}


async def simulate_latency() -> None:
    await asyncio.sleep(random.uniform(0.1, 0.5))


def random_transaction_id() -> str:
    return "TXN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def should_fail() -> bool:
    return random.random() < 0.1


@app.post("/api/v1/transactions/validate")
async def validate_transaction(payload: dict) -> dict:
    await simulate_latency()
    if should_fail():
        raise HTTPException(status_code=503, detail="Service unavailable")
    amount = payload.get("amount", 0)
    if amount <= 0:
        return {"status": "rejected", "reason": "Monto inválido"}
    return {"status": "approved"}


@app.post("/api/v1/transactions/execute")
async def execute_transaction(payload: dict) -> dict:
    await simulate_latency()
    if should_fail():
        raise HTTPException(status_code=503, detail="Service unavailable")
    transaction_id = random_transaction_id()
    status = random.choices(["pending", "completed", "failed"], weights=[0.2, 0.7, 0.1])[0]
    record = {
        "transaction_id": transaction_id,
        "status": status,
        "recipient_phone": payload.get("recipient_phone"),
        "amount": payload.get("amount"),
        "currency": payload.get("currency", "COP"),
        "created_at": datetime.utcnow().isoformat(),
    }
    transactions_store[transaction_id] = record
    return record


@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction(transaction_id: str) -> dict:
    await simulate_latency()
    if should_fail():
        raise HTTPException(status_code=503, detail="Service unavailable")
    transaction = transactions_store.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
