# Merchant of Record (MoR) Architecture for Freely

## Vision: LLM/AI Payment Platform

Freely is evolving into a **Merchant of Record platform** specifically designed for LLM/AI solutions, targeting:
- Freelancers building AI tools
- Digital nomads creating SaaS products
- Digital creators monetizing AI content
- Micro SaaS founders launching AI APIs

## Core Value Proposition

Unlike generic payment platforms, Freely provides:
- **Usage-based billing** - Track API calls, tokens, compute time
- **Subscriptions + Metering** - Combine flat fees with usage charges
- **Automatic invoicing** - Generate and send invoices for B2B customers
- **Real-time analytics** - Understand usage patterns and revenue metrics
- **Tax compliance** - Handle sales tax, VAT across jurisdictions
- **Fraud protection** - Built-in for AI API abuse prevention

## Architecture Components

### 1. Subscription Management

**Models:**
```python
class SubscriptionPlan(RecordModel):
    """Pricing plans for recurring billing."""
    organization_id: UUID
    name: str                          # "Starter", "Pro", "Enterprise"
    slug: str                          # "starter", "pro"
    description: str
    base_price_cents: int              # Monthly base fee
    currency: str                      # "usd"
    billing_period: str                # "monthly", "yearly"

    # Usage limits
    included_api_calls: int | None     # Free tier: 1000 calls/month
    included_tokens: int | None        # Free tier: 100k tokens/month

    # Overage pricing
    price_per_api_call_cents: int | None    # $0.001 per call
    price_per_1k_tokens_cents: int | None   # $0.01 per 1k tokens

    # Features
    features: dict                     # {"rate_limit": 100, "support": "email"}
    is_active: bool
    stripe_price_id: str | None        # Stripe Price ID

class Subscription(RecordModel):
    """Customer subscriptions."""
    user_id: UUID | None
    organization_id: UUID
    plan_id: UUID

    status: str                        # "active", "canceled", "past_due", "trialing"
    current_period_start: datetime
    current_period_end: datetime

    cancel_at_period_end: bool
    canceled_at: datetime | None

    trial_start: datetime | None
    trial_end: datetime | None

    stripe_subscription_id: str
    stripe_customer_id: str
```

### 2. Usage Metering

**Models:**
```python
class APIKey(RecordModel):
    """API keys for customer usage tracking."""
    user_id: UUID | None
    organization_id: UUID
    subscription_id: UUID

    name: str                          # "Production API Key"
    key_prefix: str                    # "sk_live_"
    key_hash: str                      # SHA-256 hash

    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None

class UsageEvent(RecordModel):
    """Individual usage events for metering."""
    subscription_id: UUID
    api_key_id: UUID

    event_type: str                    # "api_call", "token_usage", "compute_time"
    quantity: int                      # Number of units consumed

    # Metadata for analytics
    endpoint: str | None               # "/v1/chat/completions"
    model: str | None                  # "claude-3-5-sonnet"
    status_code: int | None            # 200, 429, 500

    timestamp: datetime                # Event timestamp

    # Billing
    billed_at: datetime | None         # When aggregated into invoice
    invoice_id: UUID | None

class UsageAggregate(RecordModel):
    """Pre-aggregated usage for faster billing."""
    subscription_id: UUID
    event_type: str

    period_start: datetime             # Start of hour/day
    period_end: datetime               # End of hour/day

    total_quantity: int                # Sum of events in period
    event_count: int                   # Number of events

    is_billed: bool
```

### 3. Invoicing

**Models:**
```python
class Invoice(RecordModel):
    """Customer invoices."""
    organization_id: UUID
    subscription_id: UUID | None
    user_id: UUID | None

    invoice_number: str                # "INV-2025-001234"

    # Amounts
    subtotal_cents: int
    tax_cents: int
    total_cents: int
    currency: str

    # Billing period
    period_start: datetime
    period_end: datetime

    # Status
    status: str                        # "draft", "open", "paid", "void", "uncollectible"
    due_date: datetime
    paid_at: datetime | None

    # Stripe
    stripe_invoice_id: str | None
    stripe_payment_intent_id: str | None

    # Customer info
    customer_email: str
    customer_name: str | None
    billing_address: dict | None

class InvoiceLineItem(RecordModel):
    """Invoice line items."""
    invoice_id: UUID

    description: str                   # "Starter Plan - December 2025"
    quantity: int                      # For usage: number of API calls
    unit_price_cents: int
    amount_cents: int

    # Type
    item_type: str                     # "subscription", "usage", "one_time"

    # Usage details
    usage_start: datetime | None
    usage_end: datetime | None
    event_type: str | None             # "api_call", "token_usage"
```

### 4. Analytics & Insights

**Aggregated Metrics:**
```python
class RevenueMetric(RecordModel):
    """Daily/monthly revenue aggregations."""
    organization_id: UUID

    period: str                        # "2025-11-19" or "2025-11"
    period_type: str                   # "daily", "monthly"

    # Revenue breakdown
    subscription_revenue_cents: int
    usage_revenue_cents: int
    total_revenue_cents: int

    # Customer metrics
    active_subscriptions: int
    new_subscriptions: int
    churned_subscriptions: int

    # Usage metrics
    total_api_calls: int
    total_tokens: int

class CustomerInsight(RecordModel):
    """Customer usage patterns and health scores."""
    subscription_id: UUID

    # Usage trends
    avg_daily_api_calls: int
    avg_daily_tokens: int

    # Engagement
    last_api_call_at: datetime | None
    days_since_last_use: int | None

    # Health score
    health_score: int                  # 0-100
    churn_risk: str                    # "low", "medium", "high"

    # Predictions
    predicted_mrr_cents: int           # Monthly recurring revenue
    predicted_usage_overage_cents: int
```

## API Endpoints

### Subscription Management

```
POST   /v1/subscriptions/plans              # Create pricing plan
GET    /v1/subscriptions/plans              # List plans
PATCH  /v1/subscriptions/plans/{id}         # Update plan

POST   /v1/subscriptions                    # Subscribe customer to plan
GET    /v1/subscriptions                    # List user's subscriptions
GET    /v1/subscriptions/{id}               # Get subscription details
PATCH  /v1/subscriptions/{id}               # Update subscription
DELETE /v1/subscriptions/{id}               # Cancel subscription
```

### API Keys & Usage

```
POST   /v1/api-keys                         # Create API key
GET    /v1/api-keys                         # List API keys
DELETE /v1/api-keys/{id}                    # Revoke API key

POST   /v1/usage/events                     # Record usage event (called by customer's code)
GET    /v1/usage/current                    # Get current period usage
GET    /v1/usage/history                    # Historical usage
```

### Invoicing

```
GET    /v1/invoices                         # List invoices
GET    /v1/invoices/{id}                    # Get invoice details
GET    /v1/invoices/{id}/pdf                # Download PDF
POST   /v1/invoices/{id}/pay                # Pay invoice
```

### Analytics

```
GET    /v1/analytics/revenue                # Revenue metrics
GET    /v1/analytics/customers              # Customer insights
GET    /v1/analytics/usage                  # Usage patterns
GET    /v1/analytics/retention              # Churn and retention
```

## Stripe Integration

### Products & Prices

1. **Create Stripe Product** for each SubscriptionPlan
2. **Create Stripe Price** with recurring billing
3. **Create Stripe Metered Price** for usage-based charges

### Subscription Flow

```python
# 1. Customer subscribes
stripe_subscription = stripe.Subscription.create(
    customer=stripe_customer_id,
    items=[
        {"price": plan.stripe_price_id},              # Base subscription
        {"price": plan.stripe_usage_price_id},        # Usage-based billing
    ],
    metadata={"subscription_id": str(subscription.id)},
)

# 2. Record usage events
stripe.SubscriptionItem.create_usage_record(
    subscription_item_id,
    quantity=1000,  # 1000 API calls
    timestamp=int(time.time()),
)

# 3. Stripe generates invoice automatically
# Webhook: invoice.created -> handle_invoice_created()
# Webhook: invoice.payment_succeeded -> handle_payment_succeeded()
```

## Usage Tracking Flow

### Customer Integration

```javascript
// Customer's application code
const response = await fetch('https://api.customer-app.com/generate', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer sk_live_abc123...',  // Freely API key
  },
  body: JSON.stringify({
    prompt: 'Write a blog post',
  }),
});

// Behind the scenes: Customer's backend tracks usage
await fetch('https://api.freely.app/v1/usage/events', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer sk_live_abc123...',
  },
  body: JSON.stringify({
    event_type: 'api_call',
    quantity: 1,
    metadata: {
      endpoint: '/generate',
      tokens: 1500,
    },
  }),
});
```

### Aggregation Job

```python
# Hourly background job
async def aggregate_usage():
    """Aggregate usage events into UsageAggregate for billing."""
    for subscription in active_subscriptions:
        # Sum events from last hour
        total_calls = sum_events(
            subscription_id=subscription.id,
            event_type="api_call",
            start=hour_start,
            end=hour_end,
        )

        # Create aggregate
        UsageAggregate.create(
            subscription_id=subscription.id,
            event_type="api_call",
            period_start=hour_start,
            period_end=hour_end,
            total_quantity=total_calls,
        )

        # Report to Stripe for metered billing
        stripe.SubscriptionItem.create_usage_record(
            subscription.stripe_usage_item_id,
            quantity=total_calls,
            timestamp=int(hour_end.timestamp()),
        )
```

## Analytics Dashboard

### Metrics to Display

**Revenue Metrics:**
- Monthly Recurring Revenue (MRR)
- Annual Recurring Revenue (ARR)
- Average Revenue Per User (ARPU)
- Revenue by plan tier
- Usage revenue vs subscription revenue

**Customer Metrics:**
- Total active subscriptions
- Churn rate
- Customer Lifetime Value (LTV)
- Trial conversion rate

**Usage Metrics:**
- Total API calls this month
- Total tokens consumed
- Average calls per customer
- Peak usage times

**Health Metrics:**
- Failed payment rate
- Support ticket volume
- API error rate
- Customer health scores

## Implementation Phases

### Phase 1: Subscriptions (Week 5)
- ✅ Create subscription models
- ✅ Stripe subscription integration
- ✅ Subscription API endpoints
- ✅ Frontend subscription management

### Phase 2: Usage Metering (Week 6)
- ✅ API key generation and management
- ✅ Usage event tracking
- ✅ Hourly aggregation jobs
- ✅ Stripe metered billing integration

### Phase 3: Invoicing (Week 7)
- ✅ Invoice generation
- ✅ Invoice PDF generation
- ✅ Email delivery
- ✅ Payment tracking

### Phase 4: Analytics (Week 8)
- ✅ Revenue metrics aggregation
- ✅ Customer insights calculation
- ✅ Dashboard frontend
- ✅ Real-time charts

### Phase 5: Advanced Features (Week 9)
- ✅ Tax calculation (Stripe Tax)
- ✅ Multi-currency support
- ✅ Dunning management (failed payments)
- ✅ Customer portal (self-service)

## Target Customer Use Cases

### Freelancer Building AI Chatbot
- **Need:** Simple pricing, usage tracking, automatic invoicing
- **Plan:** $29/mo + $0.01 per 1k tokens
- **Features:** API keys, usage dashboard, Stripe integration

### Micro SaaS: AI Content Generator
- **Need:** Scale from 10 to 1000 customers, metered billing
- **Plan:** Free tier (1k calls/mo) → Pro ($99/mo + usage)
- **Features:** Multi-tier plans, overage pricing, analytics

### Digital Creator: AI Art API
- **Need:** B2B invoicing, bulk discounts, white-label
- **Plan:** Enterprise custom pricing
- **Features:** Custom invoices, NET 30 terms, dedicated support

## Competitive Advantages

**vs Stripe Billing:**
- Pre-built for LLM/AI use cases
- No complex configuration needed
- Built-in analytics for AI metrics

**vs Lago / Metronome:**
- Simpler setup (5 minutes vs 5 hours)
- Integrated with conversational AI
- Beautiful UI out of the box

**vs Building In-House:**
- Save 6+ months development time
- Battle-tested compliance (PCI, GDPR, SOC 2)
- Focus on your AI product, not billing infrastructure

## Revenue Model for Freely

1. **Transaction Fee:** 2.9% + $0.30 per transaction (Stripe passthrough + 0.5% margin)
2. **Platform Fee:** $99-999/mo based on monthly revenue
3. **Enterprise:** Custom pricing for high-volume customers

## Next Steps

1. Implement subscription models and Stripe integration
2. Build API key management system
3. Create usage tracking infrastructure
4. Generate invoices automatically
5. Launch analytics dashboard
6. Market to AI/LLM indie developers
