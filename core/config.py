"""Application settings and environment helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Centralized strongly-typed configuration."""

    database_url: str = Field(
        default="sqlite+aiosqlite:///./voice_framework.db",
        description="SQLAlchemy connection string (async driver)",
    )
    twilio_account_sid: Optional[str] = Field(default=None)
    twilio_auth_token: Optional[str] = Field(default=None)
    twilio_default_from: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")
    llm_temperature: float = Field(default=0.2)
    api_key: Optional[str] = Field(default=None, env="VOICE_API_KEY")
    api_key_header_name: str = Field(default="x-api-key")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
