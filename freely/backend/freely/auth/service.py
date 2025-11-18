"""Authentication service."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from freely.config import settings
from freely.kit import crypto
from freely.models import User, UserSession

if TYPE_CHECKING:
    pass


class AuthService:
    """Service for managing authentication and sessions."""

    @staticmethod
    async def create_user_session(
        session: AsyncSession,
        user: User,
    ) -> tuple[str, UserSession]:
        """
        Create a new user session.

        Returns:
            (raw_token, user_session)
        """
        raw_token, token_hash = crypto.create_session_token(settings.SECRET_KEY)
        expires_at = crypto.get_expiry_time(settings.SESSION_TTL_DAYS)

        user_session = UserSession(
            token_hash=token_hash,
            expires_at=expires_at,
            user_id=user.id,
        )

        session.add(user_session)
        await session.flush()

        # Eager load user
        user_session.user = user

        return raw_token, user_session

    @staticmethod
    async def get_user_session(
        session: AsyncSession,
        token: str,
    ) -> UserSession | None:
        """Get user session by token."""
        token_hash = crypto.hash_token(token, settings.SECRET_KEY)

        stmt = (
            select(UserSession)
            .where(
                UserSession.token_hash == token_hash,
                UserSession.deleted_at.is_(None),
            )
            .limit(1)
        )

        result = await session.execute(stmt)
        user_session = result.scalar_one_or_none()

        if user_session is None:
            return None

        # Check if expired
        if crypto.is_expired(user_session.expires_at):
            return None

        return user_session

    @staticmethod
    async def delete_user_session(
        session: AsyncSession,
        user_session: UserSession,
    ) -> None:
        """Delete (soft delete) a user session."""
        user_session.deleted_at = datetime.utcnow()
        await session.flush()

    @staticmethod
    async def create_user(
        session: AsyncSession,
        email: str,
        password: str,
        username: str | None = None,
    ) -> User:
        """
        Create a new user with password.

        For development/testing.
        """
        password_hash = crypto.hash_password(password)

        user = User(
            email=email,
            email_verified=True,  # Auto-verify in development
            password_hash=password_hash,
            username=username,
        )

        session.add(user)
        await session.flush()

        return user

    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str,
    ) -> User | None:
        """Authenticate user by email and password."""
        stmt = select(User).where(
            User.email == email,
            User.deleted_at.is_(None),
        )

        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        if user.password_hash is None:
            return None

        if not crypto.verify_password(password, user.password_hash):
            return None

        return user


# Singleton instance
auth_service = AuthService()
