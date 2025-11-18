"""Authentication dependencies for FastAPI."""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from freely.auth.models import Anonymous, AuthSubject
from freely.auth.service import auth_service
from freely.models import User


async def get_db_session(request: Request) -> AsyncSession:
    """Get database session from request state (injected by middleware)."""
    return request.state.db_session


async def get_current_user_session(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    session_token: Annotated[str | None, Cookie(alias="freely_session")] = None,
) -> AuthSubject[User | Anonymous]:
    """
    Get current authenticated user from session cookie.

    Returns AuthSubject with User if authenticated, Anonymous otherwise.
    """
    if session_token is None:
        return AuthSubject(subject=Anonymous())

    user_session = await auth_service.get_user_session(session, session_token)

    if user_session is None:
        return AuthSubject(subject=Anonymous())

    return AuthSubject(subject=user_session.user, session=user_session)


async def require_user(
    auth_subject: Annotated[AuthSubject, Depends(get_current_user_session)],
) -> AuthSubject[User]:
    """
    Require authenticated user.

    Raises 401 if not authenticated.
    """
    if auth_subject.is_anonymous:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return auth_subject  # type: ignore


# Type aliases for use in endpoints
CurrentUser = Annotated[AuthSubject[User | Anonymous], Depends(get_current_user_session)]
AuthenticatedUser = Annotated[AuthSubject[User], Depends(require_user)]
