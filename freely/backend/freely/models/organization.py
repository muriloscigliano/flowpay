"""Organization model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Model, RecordModel

if TYPE_CHECKING:
    from .analytics import RevenueMetric
    from .invoice import Invoice
    from .subscription import Subscription, SubscriptionPlan
    from .usage import APIKey
    from .user import User


# Association table for many-to-many User <-> Organization
user_organizations = Table(
    "user_organizations",
    Model.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "organization_id", ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Organization(RecordModel):
    """
    Organization (merchant account).

    Represents a business that:
    - Sells products
    - Has customers
    - Receives payments
    - Can have multiple team members (users)
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Profile
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Stripe Connect account ID
    stripe_account_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    onboarded_at: Mapped[str | None] = mapped_column(String, nullable=True)  # ISO datetime

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_organizations",
        back_populates="organizations",
        lazy="raise",
    )

    # MoR relationships
    subscription_plans: Mapped[list["SubscriptionPlan"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["APIKey"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    revenue_metrics: Mapped[list["RevenueMetric"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} slug={self.slug}>"
