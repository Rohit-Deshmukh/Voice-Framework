"""Shared FastAPI dependencies."""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from core.config import Settings, get_settings


async def require_api_key(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    """Ensure requests include the configured API key (if enabled)."""

    expected_key = settings.api_key
    if not expected_key:
        return

    header_name = settings.api_key_header_name
    provided_key = request.headers.get(header_name)
    if not provided_key:
        # Headers are case-insensitive; try lowercase alias as fallback.
        provided_key = request.headers.get(header_name.lower())

    if provided_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
