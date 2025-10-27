from __future__ import annotations

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.chat import router as chat_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.transactions import router as transactions_router
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()
setup_logging()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(transactions_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Payments conversational agent API"}
