"""User settings endpoints (BYOK)."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from shared.crypto import decrypt, encrypt
from shared.db.models import UserSettings
from shared.db.session import get_db
from sqlalchemy.orm import Session

from jobflow_api.dependencies import UserInfo, require_auth
from jobflow_api.schemas.settings import SettingsResponse, SettingsUpdateRequest

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings(
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """Get current user settings."""
    row = db.query(UserSettings).filter(UserSettings.user_id == user["id"]).first()
    return SettingsResponse(
        has_gemini_key=bool(row and row.gemini_api_key_encrypted),
    )


@router.put("", response_model=SettingsResponse)
def update_settings(
    request: SettingsUpdateRequest,
    user: UserInfo = Depends(require_auth),
    db: Session = Depends(get_db),
) -> SettingsResponse:
    """Update user settings. Validates the Gemini key before storing."""
    row = db.query(UserSettings).filter(UserSettings.user_id == user["id"]).first()
    if not row:
        row = UserSettings(user_id=user["id"])
        db.add(row)

    if request.gemini_api_key is None:
        # Remove key
        row.gemini_api_key_encrypted = None
        db.commit()
        LOGGER.info("User %s removed Gemini API key", user["id"])
        return SettingsResponse(has_gemini_key=False)

    key = request.gemini_api_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    # Validate the key with a cheap test call
    try:
        from google import genai

        client = genai.Client(api_key=key)
        client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents="Say OK",
        )
    except Exception as e:
        LOGGER.warning("Invalid Gemini key for user %s: %s", user["id"], e)
        raise HTTPException(
            status_code=400,
            detail="Invalid API key — could not connect to Gemini. Check the key and try again.",
        ) from None

    row.gemini_api_key_encrypted = encrypt(key)
    db.commit()
    LOGGER.info("User %s saved Gemini API key", user["id"])
    return SettingsResponse(has_gemini_key=True)


def get_user_gemini_key(db: Session, user_id: str) -> str | None:
    """Retrieve a user's decrypted Gemini API key, or None."""
    row = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not row or not row.gemini_api_key_encrypted:
        return None
    try:
        return decrypt(row.gemini_api_key_encrypted)
    except ValueError:
        LOGGER.warning("Failed to decrypt Gemini key for user %s", user_id)
        return None
