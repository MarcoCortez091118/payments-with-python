from __future__ import annotations

from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field(default="Payments Conversational Agent")
    environment: str = Field(default="development")
    database_url: str = Field(default="postgresql+asyncpg://payments:payments@db:5432/payments")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    use_fake_llm: bool = Field(default=True)
    transaction_api_base_url: str = Field(default="http://mock-api:8001")
    log_level: str = Field(default="INFO")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
