"""Usage metering models for API tracking and billing."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import RecordModel

if TYPE_CHECKING:
    from .organization import Organization
    from .subscription import Subscription
    from .user import User


class APIKey(RecordModel):
    """
    API keys for customer usage tracking.

    Customers use these keys to authenticate requests to their LLM/AI services.
    Usage is tracked and billed based on their subscription plan.
    """

    __tablename__ = "api_keys"

    # Ownership
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subscription_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Key details
    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # "Production API Key"
    key_prefix: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # "sk_live_abc" or "sk_test_xyz"
    key_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )  # SHA-256 hash

    # Environment
    environment: Mapped[str] = mapped_column(
        String(20), nullable=False, default="production"
    )  # "production", "development"

    # Status
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Rate limiting (requests per second)
    rate_limit: Mapped[int | None] = mapped_column(
        nullable=True
    )  # Override plan default

    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="api_keys")
    organization: Mapped["Organization"] = relationship(back_populates="api_keys")
    subscription: Mapped["Subscription"] = relationship(back_populates="api_keys")
    usage_events: Mapped[list["UsageEvent"]] = relationship(
        back_populates="api_key", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_api_keys_active", "is_active", "key_hash"),
        Index("ix_api_keys_org_env", "organization_id", "environment"),
    )

    @property
    def masked_key(self) -> str:
        """Return masked key for display (sk_live_abc••••••••)."""
        return f"{self.key_prefix}••••••••"


class UsageEvent(RecordModel):
    """
    Individual usage events for metering.

    Each API call, token usage, or compute operation generates an event.
    Events are aggregated hourly/daily for billing.
    """

    __tablename__ = "usage_events"

    # Tracking
    subscription_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    api_key_id: Mapped[UUID] = mapped_column(
        ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Event details
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "api_call", "token_usage", "compute_time"
    quantity: Mapped[int] = mapped_column(nullable=False)  # Number of units consumed

    # Request metadata (for analytics)
    endpoint: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # "/v1/chat/completions"
    method: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "POST"
    status_code: Mapped[int | None] = mapped_column(nullable=True)  # 200, 429, 500

    # LLM metadata
    model: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # "claude-3-5-sonnet"
    input_tokens: Mapped[int | None] = mapped_column(nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(nullable=True)

    # Timing
    duration_ms: Mapped[int | None] = mapped_column(nullable=True)  # Request duration
    timestamp: Mapped[datetime] = mapped_column(
        nullable=False, index=True
    )  # Event timestamp

    # Billing
    is_billed: Mapped[bool] = mapped_column(nullable=False, default=False, index=True)
    billed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    invoice_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True
    )

    # Additional metadata
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    subscription: Mapped["Subscription"] = relationship(back_populates="usage_events")
    api_key: Mapped["APIKey"] = relationship(back_populates="usage_events")

    __table_args__ = (
        Index("ix_usage_events_billing", "subscription_id", "is_billed", "timestamp"),
        Index(
            "ix_usage_events_aggregation", "subscription_id", "event_type", "timestamp"
        ),
    )


class UsageAggregate(RecordModel):
    """
    Pre-aggregated usage for faster billing and analytics.

    Hourly/daily aggregations to avoid scanning millions of individual events.
    """

    __tablename__ = "usage_aggregates"

    # Tracking
    subscription_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Event type
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "api_call", "token_usage"

    # Time period
    period_start: Mapped[datetime] = mapped_column(
        nullable=False, index=True
    )  # Start of hour/day
    period_end: Mapped[datetime] = mapped_column(
        nullable=False, index=True
    )  # End of hour/day
    granularity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "hourly", "daily"

    # Aggregated data
    total_quantity: Mapped[int] = mapped_column(nullable=False)  # Sum of quantities
    event_count: Mapped[int] = mapped_column(nullable=False)  # Number of events
    unique_api_keys: Mapped[int] = mapped_column(
        nullable=False, default=1
    )  # Distinct keys used

    # Statistics
    avg_quantity: Mapped[int | None] = mapped_column(nullable=True)
    max_quantity: Mapped[int | None] = mapped_column(nullable=True)
    min_quantity: Mapped[int | None] = mapped_column(nullable=True)

    # Billing
    is_billed: Mapped[bool] = mapped_column(nullable=False, default=False)
    billed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Additional metadata
    metadata: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # {"errors": 5, "avg_duration_ms": 250}

    # Relationships
    subscription: Mapped["Subscription"] = relationship()

    __table_args__ = (
        Index(
            "ix_usage_aggregates_unique",
            "subscription_id",
            "event_type",
            "period_start",
            unique=True,
        ),
        Index("ix_usage_aggregates_billing", "subscription_id", "is_billed"),
    )
