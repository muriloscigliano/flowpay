"""Invoice models for billing and payments."""

import secrets
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


class Invoice(RecordModel):
    """
    Customer invoices for subscriptions and usage.

    Generated monthly for subscription fees + usage overages.
    """

    __tablename__ = "invoices"

    # Customer
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subscription_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Invoice details
    invoice_number: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )  # "INV-2025-001234"

    # Amounts (in cents)
    subtotal_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    tax_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    discount_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    total_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    amount_paid_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    amount_due_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="usd")

    # Billing period
    period_start: Mapped[datetime] = mapped_column(nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(nullable=False, index=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )
    # Possible values: "draft", "open", "paid", "void", "uncollectible"

    # Dates
    due_date: Mapped[datetime] = mapped_column(nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)
    voided_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Payment attempts
    attempt_count: Mapped[int] = mapped_column(nullable=False, default=0)
    next_payment_attempt: Mapped[datetime | None] = mapped_column(nullable=True)

    # Stripe integration
    stripe_invoice_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    stripe_hosted_invoice_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    stripe_invoice_pdf_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Customer information (snapshot at invoice time)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Tax details
    tax_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # VAT/GST ID
    tax_rate: Mapped[int | None] = mapped_column(
        nullable=True
    )  # Percentage * 100 (e.g., 2000 = 20%)

    # Notes
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    footer: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Metadata
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="invoices")
    subscription: Mapped["Subscription | None"] = relationship(back_populates="invoices")
    user: Mapped["User | None"] = relationship(back_populates="invoices")
    line_items: Mapped[list["InvoiceLineItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_invoices_status_due", "status", "due_date"),
        Index("ix_invoices_period", "period_start", "period_end"),
    )

    @staticmethod
    def generate_invoice_number(year: int | None = None) -> str:
        """Generate unique invoice number: INV-2025-ABC123."""
        if year is None:
            year = datetime.now().year
        random_part = secrets.token_hex(3).upper()
        return f"INV-{year}-{random_part}"

    @property
    def total_display(self) -> str:
        """Human-readable total amount."""
        dollars = self.total_cents / 100
        return f"${dollars:.2f}"

    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.status == "paid"

    @property
    def is_overdue(self) -> bool:
        """Check if invoice is past due date."""
        from datetime import timezone

        now = datetime.now(timezone.utc)
        return self.status == "open" and self.due_date < now


class InvoiceLineItem(RecordModel):
    """
    Individual line items on an invoice.

    Can represent subscription fees, usage charges, or one-time fees.
    """

    __tablename__ = "invoice_line_items"

    # Invoice
    invoice_id: Mapped[UUID] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Item details
    description: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # "Starter Plan - December 2025"
    quantity: Mapped[int] = mapped_column(
        nullable=False, default=1
    )  # For usage: number of API calls
    unit_price_cents: Mapped[int] = mapped_column(nullable=False)
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="usd")

    # Type
    item_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "subscription", "usage", "one_time", "discount"

    # Usage details (for usage line items)
    usage_start: Mapped[datetime | None] = mapped_column(nullable=True)
    usage_end: Mapped[datetime | None] = mapped_column(nullable=True)
    event_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # "api_call", "token_usage"

    # Tax
    taxable: Mapped[bool] = mapped_column(nullable=False, default=True)
    tax_rate: Mapped[int | None] = mapped_column(nullable=True)
    tax_amount_cents: Mapped[int] = mapped_column(nullable=False, default=0)

    # Metadata
    metadata: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # {"plan_name": "Starter", "overage": True}

    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="line_items")

    @property
    def amount_display(self) -> str:
        """Human-readable amount."""
        dollars = self.amount_cents / 100
        return f"${dollars:.2f}"
