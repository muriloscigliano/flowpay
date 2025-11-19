"""Analytics models for metrics and insights."""

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


class RevenueMetric(RecordModel):
    """
    Aggregated revenue metrics for analytics.

    Pre-computed daily/monthly metrics for dashboard performance.
    """

    __tablename__ = "revenue_metrics"

    # Organization
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Time period
    period: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # "2025-11-19" or "2025-11"
    period_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "daily", "monthly", "yearly"

    # Revenue breakdown (in cents)
    subscription_revenue_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    usage_revenue_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    one_time_revenue_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    total_revenue_cents: Mapped[int] = mapped_column(nullable=False, default=0)

    # Refunds and discounts
    refund_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    discount_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    net_revenue_cents: Mapped[int] = mapped_column(nullable=False, default=0)

    # Customer metrics
    active_subscriptions: Mapped[int] = mapped_column(nullable=False, default=0)
    new_subscriptions: Mapped[int] = mapped_column(nullable=False, default=0)
    churned_subscriptions: Mapped[int] = mapped_column(nullable=False, default=0)
    trial_subscriptions: Mapped[int] = mapped_column(nullable=False, default=0)

    # Usage metrics
    total_api_calls: Mapped[int] = mapped_column(nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(nullable=False, default=0)
    total_compute_minutes: Mapped[int] = mapped_column(nullable=False, default=0)
    unique_api_keys_used: Mapped[int] = mapped_column(nullable=False, default=0)

    # Invoice metrics
    invoices_sent: Mapped[int] = mapped_column(nullable=False, default=0)
    invoices_paid: Mapped[int] = mapped_column(nullable=False, default=0)
    invoices_failed: Mapped[int] = mapped_column(nullable=False, default=0)

    # Additional metrics
    metadata: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # {"avg_revenue_per_user_cents": 4500}

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="revenue_metrics")

    __table_args__ = (
        Index(
            "ix_revenue_metrics_unique", "organization_id", "period", "period_type", unique=True
        ),
    )

    @property
    def mrr_cents(self) -> int:
        """Monthly Recurring Revenue (for monthly periods)."""
        if self.period_type == "monthly":
            return self.subscription_revenue_cents
        return 0

    @property
    def arr_cents(self) -> int:
        """Annual Recurring Revenue."""
        if self.period_type == "monthly":
            return self.subscription_revenue_cents * 12
        elif self.period_type == "yearly":
            return self.subscription_revenue_cents
        return 0

    @property
    def total_revenue_display(self) -> str:
        """Human-readable total revenue."""
        dollars = self.total_revenue_cents / 100
        return f"${dollars:,.2f}"


class CustomerInsight(RecordModel):
    """
    Customer usage patterns and health scores.

    Calculated metrics for churn prediction and customer success.
    """

    __tablename__ = "customer_insights"

    # Subscription
    subscription_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Usage trends
    avg_daily_api_calls: Mapped[int] = mapped_column(nullable=False, default=0)
    avg_daily_tokens: Mapped[int] = mapped_column(nullable=False, default=0)
    avg_daily_compute_minutes: Mapped[int] = mapped_column(nullable=False, default=0)

    # Usage compared to limits
    api_calls_utilization_pct: Mapped[int | None] = mapped_column(
        nullable=True
    )  # 0-100
    tokens_utilization_pct: Mapped[int | None] = mapped_column(nullable=True)

    # Engagement metrics
    last_api_call_at: Mapped[datetime | None] = mapped_column(nullable=True)
    days_since_last_use: Mapped[int | None] = mapped_column(nullable=True)
    active_api_keys_count: Mapped[int] = mapped_column(nullable=False, default=0)

    # Financial metrics
    lifetime_value_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    avg_monthly_spend_cents: Mapped[int] = mapped_column(nullable=False, default=0)

    # Health score (0-100)
    health_score: Mapped[int] = mapped_column(
        nullable=False, default=50, index=True
    )  # 0-100
    churn_risk: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium", index=True
    )  # "low", "medium", "high"

    # Churn factors
    has_recent_usage: Mapped[bool] = mapped_column(
        nullable=False, default=True
    )  # Used in last 7 days
    has_payment_failures: Mapped[bool] = mapped_column(nullable=False, default=False)
    has_support_tickets: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Predictions (ML-based or rule-based)
    predicted_mrr_cents: Mapped[int | None] = mapped_column(
        nullable=True
    )  # Next month's MRR
    predicted_usage_overage_cents: Mapped[int | None] = mapped_column(
        nullable=True
    )  # Expected overage charges
    churn_probability: Mapped[int | None] = mapped_column(
        nullable=True
    )  # 0-100 probability

    # Growth indicators
    usage_trend: Mapped[str] = mapped_column(
        String(20), nullable=False, default="stable"
    )  # "growing", "stable", "declining"
    revenue_trend: Mapped[str] = mapped_column(
        String(20), nullable=False, default="stable"
    )

    # Last calculation
    calculated_at: Mapped[datetime] = mapped_column(nullable=False)

    # Metadata
    metadata: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # Additional insights

    # Relationships
    subscription: Mapped["Subscription"] = relationship()

    @property
    def is_healthy(self) -> bool:
        """Customer is healthy if score >= 70."""
        return self.health_score >= 70

    @property
    def needs_attention(self) -> bool:
        """Customer needs attention if score < 50 or high churn risk."""
        return self.health_score < 50 or self.churn_risk == "high"


class UsagePattern(RecordModel):
    """
    Detected usage patterns for anomaly detection.

    Helps identify unusual usage spikes or potential abuse.
    """

    __tablename__ = "usage_patterns"

    # Subscription
    subscription_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Time period
    detected_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(nullable=False)
    period_end: Mapped[datetime] = mapped_column(nullable=False)

    # Pattern details
    pattern_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "spike", "steady", "declining", "irregular"

    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "api_call", "token_usage"

    # Statistics
    baseline_value: Mapped[int] = mapped_column(
        nullable=False
    )  # Normal daily average
    detected_value: Mapped[int] = mapped_column(
        nullable=False
    )  # Unusual value detected
    deviation_pct: Mapped[int] = mapped_column(
        nullable=False
    )  # Percentage deviation from baseline

    # Severity
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="info"
    )  # "info", "warning", "critical"

    is_anomaly: Mapped[bool] = mapped_column(
        nullable=False, default=False, index=True
    )  # True for significant deviations

    # Actions taken
    notification_sent: Mapped[bool] = mapped_column(nullable=False, default=False)
    rate_limit_applied: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Context
    metadata: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # {"endpoints": ["/v1/chat"], "error_rate": 0.05}

    # Relationships
    subscription: Mapped["Subscription"] = relationship()

    __table_args__ = (Index("ix_usage_patterns_anomaly", "is_anomaly", "severity"),)
