"""Cryptography utilities."""

import hashlib
import secrets
from datetime import datetime, timedelta

from passlib.context import CryptContext

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(length: int = 32) -> str:
    """Generate a random token."""
    return secrets.token_urlsafe(length)


def hash_token(token: str, secret: str) -> str:
    """Hash a token with a secret using SHA-256."""
    return hashlib.sha256(f"{secret}{token}".encode()).hexdigest()


def create_session_token(secret: str) -> tuple[str, str]:
    """
    Create a session token pair.

    Returns:
        (raw_token, token_hash)
    """
    raw_token = generate_token(32)
    token_hash = hash_token(raw_token, secret)
    return raw_token, token_hash


def get_expiry_time(days: int) -> str:
    """Get ISO datetime string for expiry."""
    expires_at = datetime.utcnow() + timedelta(days=days)
    return expires_at.isoformat()


def is_expired(expires_at_iso: str) -> bool:
    """Check if a datetime ISO string is in the past."""
    expires_at = datetime.fromisoformat(expires_at_iso)
    return datetime.utcnow() > expires_at
