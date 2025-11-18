"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from freely.auth.dependencies import (
    AuthenticatedUser,
    CurrentUser,
    get_db_session,
)
from freely.auth.models import AuthSubject
from freely.auth.service import auth_service
from freely.config import settings
from freely.kit import crypto
from freely.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str | None
    is_admin: bool

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_admin=user.is_admin,
        )


# Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    """Register a new user."""
    # TODO: Check if email already exists

    user = await auth_service.create_user(
        session,
        email=request.email,
        password=request.password,
        username=request.username,
    )

    return UserResponse.from_user(user)


@router.post("/login", response_model=UserResponse)
async def login(
    request: LoginRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    """Login with email and password."""
    user = await auth_service.authenticate_user(
        session,
        email=request.email,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create session
    raw_token, user_session = await auth_service.create_user_session(session, user)

    # Set cookie
    response.set_cookie(
        key="freely_session",
        value=raw_token,
        max_age=settings.SESSION_TTL_DAYS * 24 * 60 * 60,  # Convert days to seconds
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )

    return UserResponse.from_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    auth_subject: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Logout and invalidate session."""
    if auth_subject.session:
        await auth_service.delete_user_session(session, auth_subject.session)

    # Clear cookie
    response.delete_cookie(key="freely_session")


@router.get("/me", response_model=UserResponse)
async def get_current_user(auth_subject: AuthenticatedUser) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse.from_user(auth_subject.subject)


@router.get("/me/optional", response_model=UserResponse | None)
async def get_current_user_optional(auth_subject: CurrentUser) -> UserResponse | None:
    """Get current user if authenticated, None otherwise."""
    if auth_subject.is_anonymous:
        return None

    return UserResponse.from_user(auth_subject.subject)  # type: ignore
