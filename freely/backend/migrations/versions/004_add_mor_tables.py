"""Add MoR (Merchant of Record) tables for subscriptions, usage tracking, invoicing, and analytics.

Revision ID: 004
Revises: 003
Create Date: 2025-11-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add MoR tables for subscription billing, usage tracking, invoicing, and analytics."""

    # 1. Subscription Plans
    op.create_table(
        "subscription_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Ownership
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Plan details
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        # Base pricing
        sa.Column("base_price_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="usd"),
        sa.Column("billing_period", sa.String(20), nullable=False, server_default="monthly"),
        # Usage limits (included)
        sa.Column("included_api_calls", sa.Integer, nullable=True),
        sa.Column("included_tokens", sa.Integer, nullable=True),
        sa.Column("included_compute_minutes", sa.Integer, nullable=True),
        # Overage pricing
        sa.Column("price_per_api_call_cents", sa.Integer, nullable=True),
        sa.Column("price_per_1k_tokens_cents", sa.Integer, nullable=True),
        sa.Column("price_per_compute_minute_cents", sa.Integer, nullable=True),
        # Features
        sa.Column("features", JSONB, nullable=False, server_default="{}"),
        sa.Column("trial_period_days", sa.Integer, nullable=True, server_default="0"),
        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default="true"),
        # Stripe
        sa.Column("stripe_product_id", sa.String(255), nullable=True),
        sa.Column("stripe_price_id", sa.String(255), nullable=True),
        sa.Column("stripe_usage_price_id", sa.String(255), nullable=True),
    )
    op.create_index("ix_subscription_plans_organization_id", "subscription_plans", ["organization_id"])
    op.create_index(
        "ix_subscription_plans_org_slug",
        "subscription_plans",
        ["organization_id", "slug"],
        unique=True,
    )

    # 2. Subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Customer
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Plan
        sa.Column(
            "plan_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscription_plans.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        # Status
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        # Billing period
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=False),
        # Cancellation
        sa.Column("cancel_at_period_end", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.String(500), nullable=True),
        # Trial
        sa.Column("trial_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_end", sa.DateTime(timezone=True), nullable=True),
        # Stripe
        sa.Column("stripe_subscription_id", sa.String(255), nullable=False),
        sa.Column("stripe_customer_id", sa.String(255), nullable=False),
        # Usage tracking (current period)
        sa.Column("current_api_calls", sa.Integer, nullable=False, server_default="0"),
        sa.Column("current_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("current_compute_minutes", sa.Integer, nullable=False, server_default="0"),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_organization_id", "subscriptions", ["organization_id"])
    op.create_index("ix_subscriptions_plan_id", "subscriptions", ["plan_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index(
        "ix_subscriptions_stripe_subscription_id",
        "subscriptions",
        ["stripe_subscription_id"],
        unique=True,
    )
    op.create_index("ix_subscriptions_stripe_customer_id", "subscriptions", ["stripe_customer_id"])

    # 3. API Keys
    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Ownership
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "subscription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Key details
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_prefix", sa.String(20), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False),
        sa.Column("environment", sa.String(20), nullable=False, server_default="production"),
        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        # Rate limiting
        sa.Column("rate_limit", sa.Integer, nullable=True),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index("ix_api_keys_organization_id", "api_keys", ["organization_id"])
    op.create_index("ix_api_keys_subscription_id", "api_keys", ["subscription_id"])
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)
    op.create_index("ix_api_keys_active", "api_keys", ["is_active", "key_hash"])
    op.create_index("ix_api_keys_org_env", "api_keys", ["organization_id", "environment"])

    # 4. Usage Events
    op.create_table(
        "usage_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Tracking
        sa.Column(
            "subscription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "api_key_id",
            UUID(as_uuid=True),
            sa.ForeignKey("api_keys.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Event details
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        # Request metadata
        sa.Column("endpoint", sa.String(255), nullable=True),
        sa.Column("method", sa.String(10), nullable=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        # LLM metadata
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("input_tokens", sa.Integer, nullable=True),
        sa.Column("output_tokens", sa.Integer, nullable=True),
        # Timing
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        # Billing
        sa.Column("is_billed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("billed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "invoice_id",
            UUID(as_uuid=True),
            sa.ForeignKey("invoices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_usage_events_subscription_id", "usage_events", ["subscription_id"])
    op.create_index("ix_usage_events_api_key_id", "usage_events", ["api_key_id"])
    op.create_index("ix_usage_events_event_type", "usage_events", ["event_type"])
    op.create_index("ix_usage_events_timestamp", "usage_events", ["timestamp"])
    op.create_index("ix_usage_events_is_billed", "usage_events", ["is_billed"])
    op.create_index(
        "ix_usage_events_billing",
        "usage_events",
        ["subscription_id", "is_billed", "timestamp"],
    )
    op.create_index(
        "ix_usage_events_aggregation",
        "usage_events",
        ["subscription_id", "event_type", "timestamp"],
    )

    # 5. Usage Aggregates
    op.create_table(
        "usage_aggregates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Tracking
        sa.Column(
            "subscription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Event type
        sa.Column("event_type", sa.String(50), nullable=False),
        # Time period
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("granularity", sa.String(20), nullable=False),
        # Aggregated data
        sa.Column("total_quantity", sa.Integer, nullable=False),
        sa.Column("event_count", sa.Integer, nullable=False),
        sa.Column("unique_api_keys", sa.Integer, nullable=False, server_default="1"),
        # Statistics
        sa.Column("avg_quantity", sa.Integer, nullable=True),
        sa.Column("max_quantity", sa.Integer, nullable=True),
        sa.Column("min_quantity", sa.Integer, nullable=True),
        # Billing
        sa.Column("is_billed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("billed_at", sa.DateTime(timezone=True), nullable=True),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_usage_aggregates_subscription_id", "usage_aggregates", ["subscription_id"])
    op.create_index("ix_usage_aggregates_event_type", "usage_aggregates", ["event_type"])
    op.create_index("ix_usage_aggregates_period_start", "usage_aggregates", ["period_start"])
    op.create_index("ix_usage_aggregates_period_end", "usage_aggregates", ["period_end"])
    op.create_index(
        "ix_usage_aggregates_unique",
        "usage_aggregates",
        ["subscription_id", "event_type", "period_start"],
        unique=True,
    )
    op.create_index(
        "ix_usage_aggregates_billing", "usage_aggregates", ["subscription_id", "is_billed"]
    )

    # 6. Invoices
    op.create_table(
        "invoices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Customer
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "subscription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscriptions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        # Invoice details
        sa.Column("invoice_number", sa.String(50), nullable=False),
        # Amounts
        sa.Column("subtotal_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tax_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("discount_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("amount_paid_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("amount_due_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="usd"),
        # Billing period
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        # Status
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        # Dates
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True),
        # Payment attempts
        sa.Column("attempt_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("next_payment_attempt", sa.DateTime(timezone=True), nullable=True),
        # Stripe
        sa.Column("stripe_invoice_id", sa.String(255), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(255), nullable=True),
        sa.Column("stripe_hosted_invoice_url", sa.String(500), nullable=True),
        sa.Column("stripe_invoice_pdf_url", sa.String(500), nullable=True),
        # Customer info (snapshot)
        sa.Column("customer_email", sa.String(255), nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=True),
        sa.Column("billing_address", JSONB, nullable=True),
        # Tax
        sa.Column("tax_id", sa.String(100), nullable=True),
        sa.Column("tax_rate", sa.Integer, nullable=True),
        # Notes
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("footer", sa.String(1000), nullable=True),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_invoices_organization_id", "invoices", ["organization_id"])
    op.create_index("ix_invoices_subscription_id", "invoices", ["subscription_id"])
    op.create_index("ix_invoices_user_id", "invoices", ["user_id"])
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)
    op.create_index("ix_invoices_status", "invoices", ["status"])
    op.create_index("ix_invoices_status_due", "invoices", ["status", "due_date"])
    op.create_index("ix_invoices_period", "invoices", ["period_start", "period_end"])
    op.create_index(
        "ix_invoices_stripe_invoice_id", "invoices", ["stripe_invoice_id"], unique=True
    )

    # 7. Invoice Line Items
    op.create_table(
        "invoice_line_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Invoice
        sa.Column(
            "invoice_id",
            UUID(as_uuid=True),
            sa.ForeignKey("invoices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Item details
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("unit_price_cents", sa.Integer, nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="usd"),
        # Type
        sa.Column("item_type", sa.String(50), nullable=False),
        # Usage details
        sa.Column("usage_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("usage_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=True),
        # Tax
        sa.Column("taxable", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("tax_rate", sa.Integer, nullable=True),
        sa.Column("tax_amount_cents", sa.Integer, nullable=False, server_default="0"),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_invoice_line_items_invoice_id", "invoice_line_items", ["invoice_id"])
    op.create_index("ix_invoice_line_items_item_type", "invoice_line_items", ["item_type"])

    # 8. Revenue Metrics
    op.create_table(
        "revenue_metrics",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Organization
        sa.Column(
            "organization_id",
            UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Time period
        sa.Column("period", sa.String(20), nullable=False),
        sa.Column("period_type", sa.String(20), nullable=False),
        # Revenue breakdown
        sa.Column("subscription_revenue_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("usage_revenue_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("one_time_revenue_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_revenue_cents", sa.Integer, nullable=False, server_default="0"),
        # Refunds and discounts
        sa.Column("refund_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("discount_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("net_revenue_cents", sa.Integer, nullable=False, server_default="0"),
        # Customer metrics
        sa.Column("active_subscriptions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("new_subscriptions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("churned_subscriptions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("trial_subscriptions", sa.Integer, nullable=False, server_default="0"),
        # Usage metrics
        sa.Column("total_api_calls", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_compute_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("unique_api_keys_used", sa.Integer, nullable=False, server_default="0"),
        # Invoice metrics
        sa.Column("invoices_sent", sa.Integer, nullable=False, server_default="0"),
        sa.Column("invoices_paid", sa.Integer, nullable=False, server_default="0"),
        sa.Column("invoices_failed", sa.Integer, nullable=False, server_default="0"),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_revenue_metrics_organization_id", "revenue_metrics", ["organization_id"])
    op.create_index("ix_revenue_metrics_period", "revenue_metrics", ["period"])
    op.create_index(
        "ix_revenue_metrics_unique",
        "revenue_metrics",
        ["organization_id", "period", "period_type"],
        unique=True,
    )

    # 9. Customer Insights
    op.create_table(
        "customer_insights",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Subscription
        sa.Column(
            "subscription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Usage trends
        sa.Column("avg_daily_api_calls", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_daily_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_daily_compute_minutes", sa.Integer, nullable=False, server_default="0"),
        # Utilization
        sa.Column("api_calls_utilization_pct", sa.Integer, nullable=True),
        sa.Column("tokens_utilization_pct", sa.Integer, nullable=True),
        # Engagement
        sa.Column("last_api_call_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("days_since_last_use", sa.Integer, nullable=True),
        sa.Column("active_api_keys_count", sa.Integer, nullable=False, server_default="0"),
        # Financial
        sa.Column("lifetime_value_cents", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_monthly_spend_cents", sa.Integer, nullable=False, server_default="0"),
        # Health score
        sa.Column("health_score", sa.Integer, nullable=False, server_default="50"),
        sa.Column("churn_risk", sa.String(20), nullable=False, server_default="medium"),
        # Churn factors
        sa.Column("has_recent_usage", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("has_payment_failures", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("has_support_tickets", sa.Boolean, nullable=False, server_default="false"),
        # Predictions
        sa.Column("predicted_mrr_cents", sa.Integer, nullable=True),
        sa.Column("predicted_usage_overage_cents", sa.Integer, nullable=True),
        sa.Column("churn_probability", sa.Integer, nullable=True),
        # Growth indicators
        sa.Column("usage_trend", sa.String(20), nullable=False, server_default="stable"),
        sa.Column("revenue_trend", sa.String(20), nullable=False, server_default="stable"),
        # Last calculation
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index(
        "ix_customer_insights_subscription_id", "customer_insights", ["subscription_id"], unique=True
    )
    op.create_index("ix_customer_insights_health_score", "customer_insights", ["health_score"])
    op.create_index("ix_customer_insights_churn_risk", "customer_insights", ["churn_risk"])

    # 10. Usage Patterns
    op.create_table(
        "usage_patterns",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Subscription
        sa.Column(
            "subscription_id",
            UUID(as_uuid=True),
            sa.ForeignKey("subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Time period
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        # Pattern details
        sa.Column("pattern_type", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        # Statistics
        sa.Column("baseline_value", sa.Integer, nullable=False),
        sa.Column("detected_value", sa.Integer, nullable=False),
        sa.Column("deviation_pct", sa.Integer, nullable=False),
        # Severity
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("is_anomaly", sa.Boolean, nullable=False, server_default="false"),
        # Actions
        sa.Column("notification_sent", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("rate_limit_applied", sa.Boolean, nullable=False, server_default="false"),
        # Metadata
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
    op.create_index("ix_usage_patterns_subscription_id", "usage_patterns", ["subscription_id"])
    op.create_index("ix_usage_patterns_detected_at", "usage_patterns", ["detected_at"])
    op.create_index("ix_usage_patterns_pattern_type", "usage_patterns", ["pattern_type"])
    op.create_index("ix_usage_patterns_is_anomaly", "usage_patterns", ["is_anomaly"])
    op.create_index("ix_usage_patterns_anomaly", "usage_patterns", ["is_anomaly", "severity"])


def downgrade() -> None:
    """Drop all MoR tables."""
    op.drop_table("usage_patterns")
    op.drop_table("customer_insights")
    op.drop_table("revenue_metrics")
    op.drop_table("invoice_line_items")
    op.drop_table("invoices")
    op.drop_table("usage_aggregates")
    op.drop_table("usage_events")
    op.drop_table("api_keys")
    op.drop_table("subscriptions")
    op.drop_table("subscription_plans")
