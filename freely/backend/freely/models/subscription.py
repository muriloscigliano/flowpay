"""Subscription models for usage-based billing and MoR functionality."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import RecordModel

if TYPE_CHECKING:
    from .organization import Organization
    from .user import User


class SubscriptionPlan(RecordModel):
    """
    Pricing plans for recurring billing.

    Supports hybrid pricing: base subscription fee + usage-based charges.
    Example: $29/month + $0.01 per 1,000 tokens
    """

    __tablename__ = "subscription_plans"

    # Ownership
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Plan details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Base pricing (recurring)
    base_price_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="usd"
    )  # ISO 4217
    billing_period: Mapped[str] = mapped_column(
        String(20), nullable=False, default="monthly"
    )  # "monthly", "yearly"

    # Usage limits (included in base price)
    included_api_calls: Mapped[int | None] = mapped_column(nullable=True)
    included_tokens: Mapped[int | None] = mapped_column(nullable=True)
    included_compute_minutes: Mapped[int | None] = mapped_column(nullable=True)

    # Overage pricing (usage beyond included amounts)
    price_per_api_call_cents: Mapped[int | None] = mapped_column(nullable=True)
    price_per_1k_tokens_cents: Mapped[int | None] = mapped_column(nullable=True)
    price_per_compute_minute_cents: Mapped[int | None] = mapped_column(nullable=True)

    # Features and limits
    features: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # {"rate_limit_per_second": 100, "support": "email"}

    # Trial period
    trial_period_days: Mapped[int | None] = mapped_column(nullable=True, default=0)

    # Status
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_public: Mapped[bool] = mapped_column(
        nullable=False, default=True
    )  # Public in pricing page

    # Stripe integration
    stripe_product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # For base subscription
    stripe_usage_price_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # For metered billing

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="subscription_plans")
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_subscription_plans_org_slug", "organization_id", "slug", unique=True),
    )

    @property
    def price_display(self) -> str:
        """Human-readable price display."""
        if self.base_price_cents == 0:
            return "Free"

        dollars = self.base_price_cents / 100
        period = "mo" if self.billing_period == "monthly" else "yr"
        return f"${dollars:.2f}/{period}"


class Subscription(RecordModel):
    """
    Customer subscriptions to pricing plans.

    Tracks subscription lifecycle: trial → active → canceled/past_due
    """

    __tablename__ = "subscriptions"

    # Customer
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Plan
    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscription_plans.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active", index=True
    )
    # Possible values: "trialing", "active", "past_due", "canceled", "unpaid", "incomplete"

    # Billing period
    current_period_start: Mapped[datetime] = mapped_column(nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(nullable=False)

    # Cancellation
    cancel_at_period_end: Mapped[bool] = mapped_column(nullable=False, default=False)
    canceled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Trial
    trial_start: Mapped[datetime | None] = mapped_column(nullable=True)
    trial_end: Mapped[datetime | None] = mapped_column(nullable=True)

    # Stripe integration
    stripe_subscription_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    stripe_customer_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )

    # Usage tracking (for current period)
    current_api_calls: Mapped[int] = mapped_column(nullable=False, default=0)
    current_tokens: Mapped[int] = mapped_column(nullable=False, default=0)
    current_compute_minutes: Mapped[int] = mapped_column(nullable=False, default=0)

    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="subscriptions")
    organization: Mapped["Organization"] = relationship(back_populates="subscriptions")
    plan: Mapped["SubscriptionPlan"] = relationship(back_populates="subscriptions")
    api_keys: Mapped[list["APIKey"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )
    usage_events: Mapped[list["UsageEvent"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )
    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        return self.status in ("trialing", "active")

    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period."""
        return self.status == "trialing"

    @property
    def days_until_renewal(self) -> int:
        """Days until next billing cycle."""
        from datetime import timezone

        now = datetime.now(timezone.utc)
        delta = self.current_period_end - now
        return max(0, delta.days)
