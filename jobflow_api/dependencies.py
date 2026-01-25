"""Shared dependencies for API endpoints."""

from fastapi import Header, HTTPException

from jobflow_api.config import get_settings


def verify_api_key(x_api_key: str | None = Header(None)) -> None:
    """Verify the API key for protected endpoints.

    If API_KEY is not configured, all requests are allowed (dev mode).
    If configured, requests must include matching X-API-Key header.
    """
    settings = get_settings()

    if settings.api_key is None:
        return

    if x_api_key is None or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
