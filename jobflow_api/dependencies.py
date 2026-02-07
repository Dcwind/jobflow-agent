"""Shared dependencies for API endpoints."""

from datetime import UTC, datetime
from typing import TypedDict

from fastapi import Depends, Header, HTTPException
from shared.db.session import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

from jobflow_api.config import get_settings


class UserInfo(TypedDict):
    """User information from session."""

    id: str
    email: str
    name: str | None


def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> UserInfo | None:
    """Validate session token and return user info.

    Better Auth stores sessions with tokens. We validate by checking
    the session table directly.

    Returns None if not authenticated (for optional auth endpoints).
    """
    if not authorization:
        return None

    # Better Auth uses bearer tokens
    if not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]

    # Query session and user tables (created by Better Auth)
    try:
        result = db.execute(
            text("""
                SELECT u.id, u.email, u.name
                FROM user u
                JOIN session s ON s.userId = u.id
                WHERE s.token = :token AND s.expiresAt > :now
            """),
            {"token": token, "now": datetime.now(UTC)},
        ).first()
    except Exception:
        # Tables may not exist yet or query failed
        return None

    if not result:
        return None

    return UserInfo(id=result[0], email=result[1], name=result[2])


def require_auth(user: UserInfo | None = Depends(get_current_user)) -> UserInfo:
    """Require authentication - raises 401 if not authenticated."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


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
