"""Async SQLModel engine and session helpers."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from core.config import get_settings


settings = get_settings()

# Only create engine if database is enabled
engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[sessionmaker] = None

if settings.use_database:
    engine = create_async_engine(settings.database_url, echo=False, future=True)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, autocommit=False
    )


async def init_db() -> None:
    """Create database tables on startup."""
    if not settings.use_database:
        # Database not enabled, skip initialization
        return
    
    if engine is None:
        raise RuntimeError("Database engine not initialized")
    
    async with engine.begin() as conn:  # pragma: no cover - migrations recommended for prod
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def session_scope() -> AsyncSession:
    """Async context manager that yields a session and handles cleanup."""
    if not settings.use_database or AsyncSessionLocal is None:
        raise RuntimeError("Database not enabled. Set USE_DATABASE=true to use database storage.")
    
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:  # pragma: no cover - defensive cleanup
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_session() -> AsyncSession:
    """FastAPI dependency that yields an AsyncSession."""
    async with session_scope() as session:
        yield session
