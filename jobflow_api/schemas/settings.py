"""User settings schemas."""

from pydantic import BaseModel


class SettingsResponse(BaseModel):
    """What the frontend sees — never the raw key."""

    has_gemini_key: bool


class SettingsUpdateRequest(BaseModel):
    """Update the user's Gemini API key. Send null to remove."""

    gemini_api_key: str | None = None
