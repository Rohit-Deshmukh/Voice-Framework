"""Application settings and environment helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Centralized strongly-typed configuration."""

    use_database: bool = Field(
        default=False,
        description="Enable database storage (False uses in-memory storage)",
    )
    database_url: str = Field(
        default="sqlite+aiosqlite:///./voice_framework.db",
        description="SQLAlchemy connection string (async driver)",
    )
    # Performance optimization flags
    enable_llm: bool = Field(
        default=False,
        description="Enable LLM features (naturalization, steering, sentiment). Disabling reduces resource usage.",
    )
    max_transcript_size: int = Field(
        default=1000,
        description="Maximum number of transcript entries to keep in memory per test run",
    )
    # Twilio credentials
    twilio_account_sid: Optional[str] = Field(default=None)
    twilio_auth_token: Optional[str] = Field(default=None)
    twilio_default_from: Optional[str] = Field(default=None)
    # LLM API keys (only used when enable_llm=True)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")
    llm_temperature: float = Field(default=0.2)
    # API authentication
    api_key: Optional[str] = Field(default=None, env="VOICE_API_KEY")
    api_key_header_name: str = Field(default="x-api-key")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
