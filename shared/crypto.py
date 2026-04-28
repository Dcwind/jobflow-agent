"""Simple Fernet encryption for storing user API keys at rest."""

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken


def _get_fernet() -> Fernet:
    """Derive a Fernet key from the app secret."""
    secret = os.environ.get("ENCRYPTION_SECRET") or os.environ.get("BETTER_AUTH_SECRET") or ""
    if not secret:
        raise RuntimeError("ENCRYPTION_SECRET or BETTER_AUTH_SECRET must be set")
    # Fernet needs a 32-byte URL-safe base64 key; derive from the app secret
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def encrypt(plaintext: str) -> str:
    """Encrypt a string. Returns a URL-safe base64 token."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(token: str) -> str:
    """Decrypt a token back to plaintext. Raises ValueError on bad data."""
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except InvalidToken as e:
        raise ValueError("Failed to decrypt — wrong secret or corrupted data") from e
