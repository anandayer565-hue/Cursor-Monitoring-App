"""Password hashing helpers. Never store or log plaintext passwords."""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Return a bcrypt hash string for the given plaintext password."""
    if not isinstance(password, str) or password == "":
        raise ValueError("password must be a non-empty string")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    """
    Verify plaintext against a bcrypt hash.

    Uses bcrypt's constant-time comparison. Returns False on bad inputs
    instead of raising, so callers can show a generic auth error.
    """
    if not password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False
