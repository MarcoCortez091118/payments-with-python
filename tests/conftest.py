from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def configure_settings() -> None:
    os.environ.setdefault("USE_FAKE_LLM", "true")
    os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)
    os.environ.setdefault("TRANSACTION_API_BASE_URL", "http://testserver")
    get_settings.cache_clear()


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()
