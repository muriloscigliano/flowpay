"""User model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import RecordModel

if TYPE_CHECKING:
    from .organization import Organization


class User(RecordModel):
    """
    User account.

    Represents an authenticated user who can:
    - Create and manage organizations
    - Access the dashboard
    - Use API tokens
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Profile
    username: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Password (hashed with bcrypt)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Admin flag
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        secondary="user_organizations",
        back_populates="users",
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class UserSession(RecordModel):
    """
    User session (cookie-based authentication).

    Sessions expire after 30 days by default.
    """

    __tablename__ = "user_sessions"

    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    expires_at: Mapped[str] = mapped_column(String, nullable=False)  # ISO datetime

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User", lazy="joined")
