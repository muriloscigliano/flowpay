# Freely Platform - Unified Architecture

## Platform Overview

Freely is a **dual-product platform** powered by shared MoR infrastructure:

```
Freely Platform
│
├── Freely (B2B Freelancer Billing)
│   └── Target: Designers, developers, content creators billing clients
│
└── AgentPay (B2C AI-Native MoR)
    └── Target: AI startups, SaaS, digital products selling to consumers
```

Both products share the same backend (subscriptions, usage tracking, invoicing, analytics) but serve different markets with different UX.

---

## Why One Platform?

### Shared Infrastructure
Both Freely and AgentPay need:
- ✅ Subscription management
- ✅ Usage-based billing
- ✅ Invoice generation
- ✅ Payment processing (Stripe)
- ✅ Multi-currency support
- ✅ Analytics and insights
- ✅ Customer portals

**Decision:** Build once, use twice.

### Different UX, Same Backend

**Freely:**
- Dashboard for freelancers
- Client management
- Project/hour tracking
- Manual usage entry
- B2B invoicing

**AgentPay:**
- Embeddable widgets
- AI agent system
- Automatic usage tracking (API)
- B2C checkout flows
- Self-service portals

---

## Technical Architecture

### Backend (Shared)

```
freely/backend/
├── freely/
│   ├── models/              # Database models (shared)
│   │   ├── subscription.py  # Subscriptions
│   │   ├── usage.py         # Usage tracking
│   │   ├── invoice.py       # Invoicing
│   │   ├── analytics.py     # Analytics
│   │   └── ...
│   │
│   ├── subscription/        # Subscription service (shared)
│   ├── usage/               # Usage service (shared)
│   ├── invoicing/           # Invoice service (shared)
│   │
│   ├── freely/              # Freely-specific (freelancer features)
│   │   ├── endpoints.py     # Freelancer dashboard API
│   │   └── service.py       # Client management
│   │
│   └── agentpay/            # AgentPay-specific (AI-native features)
│       ├── agents/          # Multi-agent system
│       │   ├── sales_agent.py
│       │   ├── billing_agent.py
│       │   ├── support_agent.py
│       │   └── orchestrator.py
│       │
│       ├── rag/             # RAG system for merchant data
│       │   ├── embeddings.py
│       │   └── retrieval.py
│       │
│       ├── widgets/         # Embeddable component API
│       │   ├── checkout.py
│       │   └── portal.py
│       │
│       └── endpoints.py     # AgentPay API
│
└── migrations/              # Database migrations (shared)
```

### Frontend (Separate)

```
freely/frontend/
├── app/
│   ├── pages/
│   │   ├── freely/          # Freelancer dashboard
│   │   │   ├── clients/
│   │   │   ├── projects/
│   │   │   └── invoices/
│   │   │
│   │   └── agentpay/        # AgentPay dashboard
│   │       ├── overview/
│   │       ├── agents/
│   │       └── settings/
│   │
│   └── components/
│       ├── freely/          # Freelancer components
│       └── agentpay/        # AgentPay embeddable widgets
│           ├── Checkout.vue
│           ├── CustomerPortal.vue
│           ├── AgentChat.vue
│           └── PricingTable.vue
```

### SDK (AgentPay)

```
freely/sdk/
├── javascript/              # @agentpay/js
├── python/                  # agentpay-python
├── react/                   # @agentpay/react
└── vue/                     # @agentpay/vue
```

---

## Data Model (Unified)

### Core Models (Shared)

**Users & Organizations**
- `User` - Account holder (freelancer OR merchant)
- `Organization` - Business entity (freelancer business OR SaaS company)
- `user_organizations` - Many-to-many relationship

**Subscriptions**
- `SubscriptionPlan` - Pricing plan
  - Freely: "$150/hr + $500/mo retainer"
  - AgentPay: "$29/mo + $0.01 per 1k tokens"
- `Subscription` - Active customer subscription

**Usage Tracking**
- `APIKey` - API key for usage tracking
  - Freely: Manual tracking keys
  - AgentPay: SDK keys for auto-tracking
- `UsageEvent` - Individual usage event
- `UsageAggregate` - Pre-computed aggregations

**Invoicing**
- `Invoice` - Monthly invoice
- `InvoiceLineItem` - Line items (base + usage)

**Analytics**
- `RevenueMetric` - Revenue aggregations
- `CustomerInsight` - Churn prediction, health scores
- `UsagePattern` - Anomaly detection

### AgentPay-Specific Models

**Agents**
- `Agent` - AI agent configuration
- `AgentConversation` - Agent chat history
- `AgentAction` - Actions taken by agents

**RAG**
- `MerchantKnowledge` - Ingested merchant data
- `KnowledgeEmbedding` - Vector embeddings
- `KnowledgeSource` - Data sources (FAQs, docs, policies)

**Widgets**
- `Widget` - Embeddable widget configuration
- `WidgetSession` - Widget interaction sessions
- `WidgetEvent` - User interactions tracked

**Personalization**
- `CustomerBehavior` - Behavioral tracking
- `PricingExperiment` - A/B tests
- `Recommendation` - AI-generated recommendations

---

## API Architecture

### Shared Endpoints

```
/v1/subscriptions/*         # Subscription management
/v1/usage/*                  # Usage tracking
/v1/invoices/*               # Invoice operations
/v1/analytics/*              # Analytics data
```

### Freely-Specific Endpoints

```
/v1/freely/clients/*         # Client management
/v1/freely/projects/*        # Project tracking
/v1/freely/timesheets/*      # Manual time entry
```

### AgentPay-Specific Endpoints

```
/v1/agentpay/agents/*        # Agent management
/v1/agentpay/widgets/*       # Widget configuration
/v1/agentpay/checkout/*      # Checkout API
/v1/agentpay/embed/*         # Embeddable components
/v1/agentpay/rag/*           # RAG knowledge management
```

---

## Deployment Strategy

### Single Deployment (Current)

```
freely-platform.com
├── /                        # Marketing site
├── /freely/*                # Freelancer dashboard
├── /agentpay/*              # AgentPay dashboard
├── /api/*                   # Unified API
└── /embed/*                 # Embeddable widgets
```

### Separate Later (If Needed)

```
freely.com                   # Freelancer product
agentpay.com                 # AI-native MoR product

Shared:
api.freely-platform.com      # Unified backend API
```

---

## Development Roadmap

### Already Built ✅
- User authentication
- Organization multi-tenancy
- Subscription system
- Usage tracking models
- Invoice generation
- Analytics models
- Stripe integration
- Database migrations

### Phase 1: Freelancer Features (Freely)
**Timeline:** 2 weeks

- [ ] Client management
- [ ] Project tracking
- [ ] Manual usage entry (hours, projects)
- [ ] Freelancer dashboard
- [ ] Client portal
- [ ] Invoice customization

### Phase 2: Agent System (AgentPay)
**Timeline:** 3 weeks

- [ ] Base agent architecture
- [ ] Sales Agent (checkout assistant)
- [ ] Billing Agent (invoice explainer)
- [ ] Support Agent (customer service)
- [ ] RAG system for merchant data
- [ ] Agent orchestration

### Phase 3: Embeddable Widgets (AgentPay)
**Timeline:** 2 weeks

- [ ] React SDK
- [ ] Vue SDK
- [ ] JavaScript SDK
- [ ] Checkout widget
- [ ] Customer portal widget
- [ ] Agent chat widget
- [ ] Usage meter widget

### Phase 4: Advanced Intelligence (AgentPay)
**Timeline:** 3 weeks

- [ ] Churn prediction
- [ ] Usage forecasting
- [ ] Personalized pricing
- [ ] A/B testing engine
- [ ] Behavioral insights
- [ ] Recommendation system

### Phase 5: Global MoR (Both)
**Timeline:** 2 weeks

- [ ] Multi-currency support
- [ ] Automatic tax calculation
- [ ] Stablecoin payouts
- [ ] Cross-border compliance
- [ ] FX optimization

---

## Revenue Model

### Freely (Freelancer Billing)

**Pricing:**
- Free: Up to $1,000/mo processed
- Pro: $99/mo - Up to $10,000/mo
- Scale: $499/mo - Up to $100,000/mo
- Transaction fee: 2.9% + $0.30

**Target Revenue:**
- Year 1: $500K ARR (5,000 freelancers × $100/mo avg)
- Year 3: $5M ARR (50,000 freelancers)

### AgentPay (AI-Native MoR)

**Pricing:**
- Starter: Free up to $1,000 MRR (2.9% + $0.30)
- Pro: $99/mo up to $10,000 MRR (2.5% + $0.30)
- Scale: $499/mo up to $100,000 MRR (2.0% + $0.30)
- Enterprise: Custom

**Target Revenue:**
- Year 1: $1M ARR (1,000 merchants × $1,000 avg)
- Year 3: $20M ARR (10,000 merchants)

### Combined Platform
- Year 1: $1.5M ARR
- Year 3: $25M ARR
- Year 5: $100M ARR (exit/IPO target)

---

## Market Positioning

### Freely
**Competing with:**
- Harvest, Toggl, FreshBooks (time tracking + invoicing)
- Bonsai, HoneyBook (freelancer management)

**Advantage:**
- Usage-based billing (not just time tracking)
- Beautiful client portals
- Integrated payments

**Market:** 70M freelancers in US, $1.3T economy

### AgentPay
**Competing with:**
- Stripe (no MoR, no AI)
- Paddle, FastSpring (MoR but no AI)
- Chargebee, Recurly (billing but no MoR or AI)

**Advantage:**
- AI-native intelligence
- Multi-agent system
- Adaptive commerce brain

**Market:** AI/SaaS startups (explosive growth, underserved)

---

## Why This Works

### Shared Infrastructure = Lower Costs
- Build subscription system once
- Reuse for both products
- Same database, same API
- Economies of scale

### Different Markets = Lower Competition
- Freely: Compete with freelancer tools (not payment platforms)
- AgentPay: Compete with payment platforms (not freelancer tools)
- Minimal overlap

### Network Effects
- Freelancers sell to businesses (B2B)
- Businesses may need AgentPay for their own customers (B2C)
- Cross-sell opportunity

### Data Synergies
- Usage patterns from Freely inform AgentPay insights
- AgentPay AI agents can be adapted for Freely
- Compliance knowledge shared

---

## The Big Picture

**Freely Platform is the operating system for digital commerce.**

- Freelancers use Freely to bill clients
- SaaS companies use AgentPay to bill customers
- Both use same MoR infrastructure
- Both benefit from AI intelligence
- Both scale together

**One platform. Two products. Unlimited potential.**

---

**Status:** Foundation Complete
**Next:** Implement Freely freelancer features OR AgentPay agent system
**Your choice!** 🚀
