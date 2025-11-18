# Freely Rebuild Architecture Plan
## Complete From-Scratch Implementation Guide

**Decision:** Nuxt 4 + Vue 3 frontend, Python/FastAPI backend
**Goal:** Rebuild Polar foundation with identical UI/UX, no license attribution needed
**Timeline:** 6-8 weeks full-time

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Database Schema](#database-schema)
5. [Implementation Phases](#implementation-phases)
6. [Week-by-Week Breakdown](#week-by-week-breakdown)

---

## Tech Stack

### Backend
```yaml
Language: Python 3.12
Framework: FastAPI 0.120+
Database: PostgreSQL 16 + pgvector
Cache/Queue: Redis 7
Storage: MinIO (S3-compatible)
Background Jobs: Dramatiq + APScheduler
Payments: Stripe SDK
LLM: Anthropic Claude SDK
```

### Frontend
```yaml
Framework: Nuxt 4
Language: TypeScript 5.7+
UI: Vue 3.5
Styling: Tailwind CSS v4
Components: Radix Vue + Custom
State: Pinia
Forms: VeeValidate
API Client: openapi-typescript + ofetch
Animations: @vueuse/motion
```

### DevOps
```yaml
Containerization: Docker + Docker Compose
CI/CD: GitHub Actions
Deployment: DigitalOcean App Platform
Monitoring: Sentry
```

---

## Backend Architecture

### Directory Structure

```
server/
├── freely/                      # Main package (renamed from polar)
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py             # Base model classes
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── product.py
│   │   ├── product_price.py
│   │   ├── subscription.py
│   │   ├── order.py
│   │   ├── customer.py
│   │   ├── payment.py
│   │   ├── refund.py
│   │   └── ...                 # 64 total models
│   ├── account/                # Account management module
│   │   ├── endpoints.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   └── auth.py
│   ├── product/                # Product module
│   ├── subscription/           # Subscription module
│   ├── order/                  # Order module
│   ├── customer/               # Customer module
│   ├── auth/                   # Authentication system
│   │   ├── models.py           # AuthSubject, scopes
│   │   ├── dependencies.py     # Authenticator factory
│   │   ├── middlewares.py      # AuthSubjectMiddleware
│   │   ├── service.py          # Session management
│   │   └── scope.py            # Scope definitions
│   ├── integrations/           # External integrations
│   │   ├── stripe/
│   │   │   ├── service.py      # Stripe API wrapper (1000+ lines)
│   │   │   ├── endpoints.py    # Webhook endpoints
│   │   │   ├── tasks.py        # Webhook processors
│   │   │   └── payment.py      # Payment handlers
│   │   └── anthropic/
│   │       └── client.py       # Claude integration
│   ├── agent_core/             # AgentPay orchestrator
│   │   ├── orchestrator.py     # 6-layer message processing
│   │   └── tools.py            # Tool definitions
│   ├── agent_llm/              # LLM integrations
│   │   └── anthropic_client.py
│   ├── agent_knowledge/        # RAG system
│   │   └── vector_store.py     # pgvector search
│   ├── kit/                    # Shared utilities
│   │   ├── db/                 # Database utilities
│   │   ├── jwt.py
│   │   ├── crypto.py
│   │   └── utils.py
│   ├── worker/                 # Background jobs
│   │   ├── __init__.py         # Dramatiq setup
│   │   └── tasks.py
│   ├── migrations/             # Alembic migrations
│   │   └── versions/
│   ├── config.py               # Settings (Pydantic)
│   ├── app.py                  # FastAPI app factory
│   └── api.py                  # Router aggregation
├── tests/                      # pytest tests
├── scripts/                    # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml              # uv dependencies
└── alembic.ini

clients/
├── apps/
│   └── web/                    # Nuxt app
│       ├── app/                # Nuxt app directory
│       │   ├── pages/          # File-based routes
│       │   ├── layouts/        # Layouts
│       │   ├── components/     # Vue components
│       │   └── composables/    # Composables
│       ├── server/             # Server routes/middleware
│       ├── public/             # Static assets
│       ├── assets/             # Processed assets
│       ├── nuxt.config.ts
│       ├── tailwind.config.ts
│       └── package.json
└── packages/
    ├── ui/                     # Shared UI library
    │   ├── components/
    │   │   ├── atoms/          # 32 custom components
    │   │   └── ui/             # 26 Radix Vue components
    │   ├── composables/
    │   └── utils/
    └── sdk/                    # Public SDK
```

### Core Patterns

#### 1. Modular Domain Structure
Each domain (product, subscription, order, etc.) follows this pattern:

```python
# product/endpoints.py
from fastapi import APIRouter, Depends
from .service import ProductService
from .auth import ProductRead, ProductWrite
from .schemas import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_create: ProductCreate,
    auth_subject: ProductWrite,  # Dependency injection
    session: AsyncSession = Depends(get_db_session),
) -> Product:
    return await ProductService.create(session, product_create, auth_subject)
```

```python
# product/service.py
class ProductService:
    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        create: ProductCreate,
        auth_subject: AuthSubject[User | Organization],
    ) -> Product:
        # 1. Validate permissions
        # 2. Create product
        # 3. Create prices
        # 4. Sync to Stripe
        # 5. Trigger webhooks
        # NO session.commit() - handled by middleware
        return product
```

```python
# product/repository.py
class ProductRepository(RepositoryBase[Product]):
    model = Product

    def get_readable_statement(
        self, auth_subject: AuthSubject[User | Organization]
    ) -> Select[tuple[Product]]:
        statement = self.get_base_statement()

        if is_user(auth_subject):
            # Filter to user's organizations
            statement = statement.where(Product.organization_id.in_(...))
        elif is_organization(auth_subject):
            statement = statement.where(Product.organization_id == auth_subject.subject.id)

        return statement
```

#### 2. Authentication Pattern

```python
# auth/models.py
@dataclass
class AuthSubject(Generic[S]):
    subject: S  # User | Organization | Customer | Anonymous
    scopes: set[Scope]
    session: Session | None

# auth/dependencies.py
def Authenticator(
    allowed_subjects: set[SubjectType],
    required_scopes: set[Scope] | None = None,
) -> Callable:
    # Returns dependency that validates subject type + scopes
    # Injects into OpenAPI docs
    ...

# product/auth.py
_ProductWrite = Authenticator(
    allowed_subjects={User, Organization},
    required_scopes={Scope.web_write, Scope.products_write},
)
ProductWrite = Annotated[AuthSubject[User | Organization], Depends(_ProductWrite)]
```

#### 3. Database Models

```python
# models/base.py
class Model(DeclarativeBase):
    """SQLAlchemy 2.0 base"""
    pass

class TimestampedModel(Model):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    modified_at: Mapped[datetime | None] = mapped_column(onupdate=utc_now)
    deleted_at: Mapped[datetime | None]  # Soft deletion

class IDModel(Model):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

class RecordModel(IDModel, TimestampedModel):
    """Most models inherit from this"""
    __abstract__ = True
```

```python
# models/product.py
class Product(RecordModel):
    __tablename__ = "products"

    name: Mapped[str]
    description: Mapped[str | None]
    is_archived: Mapped[bool] = mapped_column(default=False)

    stripe_product_id: Mapped[str | None]

    recurring_interval: Mapped[SubscriptionRecurringInterval | None]
    is_tax_applicable: Mapped[bool] = mapped_column(default=True)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))

    # Relationships
    organization: Mapped["Organization"] = relationship(lazy="raise")
    prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="product",
        lazy="raise",
        order_by="ProductPrice.created_at",
    )

    @hybrid_property
    def is_recurring(self) -> bool:
        return self.recurring_interval is not None
```

#### 4. Stripe Integration

```python
# integrations/stripe/service.py
import stripe as stripe_lib

stripe_lib.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    # Account management (Connect)
    async def create_account(self, account: AccountCreate, name: str) -> stripe_lib.Account:
        return await stripe_lib.Account.create_async(
            country=account.country,
            type="express",
            capabilities={"transfers": {"requested": True}},
            settings={"payouts": {"schedule": {"interval": "manual"}}},
        )

    # Products
    async def create_product(self, name: str, description: str | None) -> stripe_lib.Product:
        return await stripe_lib.Product.create_async(name=name, description=description)

    # Subscriptions
    async def create_out_of_band_subscription(
        self, customer: str, prices: list[str], currency: str
    ) -> tuple[stripe_lib.Subscription, stripe_lib.Invoice]:
        subscription = await stripe_lib.Subscription.create_async(
            customer=customer,
            currency=currency,
            collection_method="send_invoice",  # Platform controls payment
            days_until_due=0,
            items=[{"price": price, "quantity": 1} for price in prices],
        )
        # Mark invoice as paid out-of-band
        invoice = await self._pay_out_of_band_invoice(subscription.latest_invoice.id)
        return subscription, invoice
```

#### 5. Background Jobs

```python
# worker/__init__.py
import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries

redis_broker = RedisBroker(url=settings.REDIS_URL)
redis_broker.add_middleware(AgeLimit())
redis_broker.add_middleware(TimeLimit())
redis_broker.add_middleware(Retries(max_retries=20, min_backoff=2000))
dramatiq.set_broker(redis_broker)

@dramatiq.actor(actor_name="subscription.cycle", priority=TaskPriority.LOW)
async def subscription_cycle(subscription_id: UUID) -> None:
    async with AsyncSessionMaker() as session:
        repository = SubscriptionRepository.from_session(session)
        subscription = await repository.get_by_id(subscription_id)
        # Process subscription
        # No session.commit() - handled by middleware
```

---

## Frontend Architecture

### Nuxt 4 Structure

```
app/
├── pages/
│   ├── index.vue                    # Home page
│   ├── dashboard/
│   │   └── [organization]/
│   │       ├── index.vue            # Dashboard home
│   │       ├── products/
│   │       │   ├── index.vue
│   │       │   └── [id].vue
│   │       ├── customers.vue
│   │       └── settings.vue
│   ├── [organization]/              # Public storefront
│   │   ├── index.vue
│   │   └── portal/                  # Customer portal
│   │       └── index.vue
│   └── checkout/
│       └── [id].vue
├── layouts/
│   ├── default.vue                  # Base layout
│   ├── dashboard.vue                # Dashboard layout
│   └── portal.vue                   # Customer portal layout
├── components/
│   ├── Dashboard/
│   │   ├── DashboardSidebar.vue
│   │   ├── DashboardHeader.vue
│   │   └── DashboardBody.vue
│   ├── Products/
│   │   ├── ProductList.vue
│   │   ├── ProductCard.vue
│   │   └── ProductForm.vue
│   └── UI/                          # From packages/ui
│       └── (auto-imported)
├── composables/
│   ├── useAuth.ts                   # Auth state
│   ├── useOrganization.ts           # Org context
│   ├── api/
│   │   ├── useProducts.ts
│   │   ├── useSubscriptions.ts
│   │   └── useCustomers.ts
│   └── useSSE.ts                    # Server-sent events
├── middleware/
│   ├── auth.ts                      # Route protection
│   └── organization.ts              # Org membership check
├── server/
│   ├── api/
│   │   └── [...].ts                 # Proxy to FastAPI
│   └── middleware/
│       └── cors.ts
├── stores/
│   ├── auth.ts                      # Pinia store
│   └── theme.ts                     # Dark mode
├── utils/
│   ├── api.ts                       # API client factory
│   └── types.ts                     # Shared types
└── assets/
    └── styles/
        └── globals.css              # Tailwind + custom styles
```

### Core Patterns

#### 1. API Client (OpenAPI TypeScript)

```typescript
// utils/api.ts
import createClient from 'openapi-fetch'
import type { paths } from '@freely/types'  // Generated

export function createFreelyAPI(baseURL: string, token?: string) {
  return createClient<paths>({
    baseURL,
    credentials: 'include',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
}

export const api = createFreelyAPI(
  import.meta.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000'
)

// Error handling
export async function unwrap<T>(promise: Promise<{ data?: T; error?: any }>) {
  const { data, error } = await promise
  if (error) throw error
  if (!data) throw new Error('No data returned')
  return data
}
```

#### 2. Composables (Data Fetching)

```typescript
// composables/api/useProducts.ts
export function useProducts(organizationId: MaybeRef<string>, params?: Ref<ProductListParams>) {
  return useAsyncData(
    `products-${unref(organizationId)}`,
    () => unwrap(api.GET('/v1/products/', {
      params: {
        query: {
          organization_id: unref(organizationId),
          ...unref(params),
        },
      },
    })),
    {
      watch: [() => unref(params)],
      server: true,  // SSR
    }
  )
}

export function useProduct(id: MaybeRef<string | undefined>) {
  return useAsyncData(
    `product-${unref(id)}`,
    () => {
      const productId = unref(id)
      if (!productId) return null
      return unwrap(api.GET('/v1/products/{id}', {
        params: { path: { id: productId } },
      }))
    },
    {
      watch: [() => unref(id)],
    }
  )
}
```

#### 3. Pinia Stores

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserRead | null>(null)
  const organizations = ref<Organization[]>([])

  const authenticated = computed(() => user.value !== null)

  async function loadUser() {
    const data = await unwrap(api.GET('/v1/users/me'))
    user.value = data
  }

  async function logout() {
    await api.POST('/v1/auth/logout')
    user.value = null
    navigateTo('/login')
  }

  return { user, organizations, authenticated, loadUser, logout }
})
```

#### 4. Layouts

```vue
<!-- layouts/dashboard.vue -->
<template>
  <div class="flex h-screen">
    <DashboardSidebar :organization="organization" />
    <main class="flex-1 overflow-y-auto">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const organizationSlug = computed(() => route.params.organization as string)
const { data: organization } = await useOrganization(organizationSlug)

if (!organization.value) {
  throw createError({ statusCode: 404, message: 'Organization not found' })
}

provide('organization', organization)
</script>
```

#### 5. Pages

```vue
<!-- pages/dashboard/[organization]/products/index.vue -->
<template>
  <div>
    <DashboardBody title="Products">
      <ProductList :products="products" @create="showCreateDialog = true" />
    </DashboardBody>

    <ProductCreateDialog v-model="showCreateDialog" :organization="organization" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: ['auth', 'organization'],
})

const route = useRoute()
const organization = inject<Ref<Organization>>('organization')
const showCreateDialog = ref(false)

const { data: products, refresh } = await useProducts(organization.value.id)
</script>
```

---

## Database Schema

### Critical Tables (Minimum Viable)

**Phase 1 (Core Commerce):**
1. users
2. oauth_accounts
3. organizations
4. accounts (Stripe Connect)
5. products
6. product_prices (polymorphic)
7. customers
8. checkouts
9. orders
10. payments
11. subscriptions
12. payment_methods

**Phase 2 (Extended Features):**
13. discounts
14. discount_redemptions
15. benefits
16. benefit_grants
17. refunds
18. webhooks

**Phase 3 (AgentPay):**
19. conversations
20. messages
21. product_embeddings (pgvector)

### Key Relationships

```
Organization
├── has many Products
├── has many Customers
├── has one Account (Stripe Connect)
└── has many Orders

Product
├── belongs to Organization
├── has many ProductPrices
└── has many Orders

Customer
├── belongs to Organization
├── has many Orders
├── has many Subscriptions
└── has many PaymentMethods

Subscription
├── belongs to Customer
├── belongs to Product
├── has many Orders
└── has one PaymentMethod

Order
├── belongs to Customer
├── belongs to Product
├── belongs to Subscription (optional)
└── has one Payment

Payment
├── belongs to Order
└── belongs to Organization
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Backend:**
- ✅ Project setup (uv, FastAPI, SQLAlchemy)
- ✅ Database models (12 core tables)
- ✅ Authentication system (AuthSubject, sessions, scopes)
- ✅ Base repository pattern
- ✅ Alembic migrations
- ✅ Docker Compose (PostgreSQL, Redis, MinIO)

**Frontend:**
- ✅ Nuxt 4 setup
- ✅ Tailwind CSS v4 + OKLCH colors (copy Polar's globals.css)
- ✅ 26 Radix Vue components (shadcn/ui equivalent)
- ✅ Dark mode
- ✅ OpenAPI client generation

**Deliverables:**
- Working dev environment
- Login/logout flow
- Basic dashboard shell

---

### Phase 2: Core Commerce (Week 3-4)

**Backend:**
- ✅ Product module (CRUD + Stripe sync)
- ✅ Customer module (CRUD + Stripe customers)
- ✅ Checkout module (Payment Intent, Setup Intent)
- ✅ Order module (invoice creation)
- ✅ Stripe webhook handling (15+ events)

**Frontend:**
- ✅ Product catalog pages
- ✅ Product create/edit forms
- ✅ Customer list/detail
- ✅ Checkout flow
- ✅ Order history

**Deliverables:**
- Can create products
- Can create customers
- Can complete checkout
- Stripe integration working

---

### Phase 3: Subscriptions (Week 5)

**Backend:**
- ✅ Subscription module (create, update, cancel)
- ✅ Out-of-band subscription flow
- ✅ Subscription lifecycle (webhooks)
- ✅ Background workers (subscription cycling)

**Frontend:**
- ✅ Subscription management UI
- ✅ Customer portal (manage subscriptions)
- ✅ Billing history

**Deliverables:**
- Recurring billing working
- Customer can manage subscriptions
- Webhooks processing correctly

---

### Phase 4: AgentPay Chat (Week 6)

**Backend:**
- ✅ Agent orchestrator (6-layer system)
- ✅ Anthropic Claude integration
- ✅ RAG with pgvector
- ✅ Conversation/message models
- ✅ SSE streaming

**Frontend:**
- ✅ Chat widget component
- ✅ Conversation history
- ✅ Product indexing UI

**Deliverables:**
- AI chat working
- Product recommendations
- Conversational commerce

---

### Phase 5: Polish & Deploy (Week 7-8)

**Backend:**
- ✅ Error handling
- ✅ Logging (structlog)
- ✅ Monitoring (Sentry)
- ✅ Tests (pytest)

**Frontend:**
- ✅ Loading states
- ✅ Error boundaries
- ✅ Toast notifications
- ✅ Responsive design
- ✅ Accessibility

**Deployment:**
- ✅ Production environment variables
- ✅ Database migrations
- ✅ Backend to DigitalOcean
- ✅ Frontend to Vercel/Netlify
- ✅ Domain setup (freely.you)

**Deliverables:**
- Production-ready app
- First customer onboarded
- MVP complete

---

## Week-by-Week Breakdown

### Week 1: Backend Foundation

**Day 1-2: Project Setup**
```bash
# Backend
cd server
uv init
uv add fastapi uvicorn sqlalchemy asyncpg alembic pydantic-settings

# Database
docker compose up -d  # PostgreSQL + Redis + MinIO

# Frontend
cd ../clients/apps/web
pnpm create nuxt@latest .
pnpm add -D tailwindcss @nuxtjs/tailwindcss
pnpm add @radix-vue/nuxt pinia
```

**Day 3-4: Database Models**
- Implement 12 core models
- Create Alembic migration
- Test database connection

**Day 5-7: Authentication**
- AuthSubject system
- Session management
- Middleware
- Login/logout endpoints

### Week 2: Frontend Foundation

**Day 1-2: Tailwind Setup**
- Copy Polar's globals.css
- Configure OKLCH colors
- Set up dark mode
- Test color system

**Day 3-5: UI Components**
- Implement 26 Radix Vue components
- Create 32 custom atoms
- Build dashboard layout
- Create sidebar navigation

**Day 6-7: API Client**
- Generate OpenAPI types
- Create API client factory
- Build composables
- Test authentication flow

### Week 3: Products & Customers

**Day 1-3: Product Module**
- Product CRUD backend
- Stripe product sync
- Product prices (polymorphic)
- Frontend product pages

**Day 4-5: Customer Module**
- Customer CRUD backend
- Stripe customer creation
- Frontend customer pages

**Day 6-7: Integration Testing**
- Test product creation flow
- Test Stripe sync
- Fix bugs

### Week 4: Checkout & Orders

**Day 1-2: Checkout Module**
- Payment Intent flow
- Setup Intent flow
- Checkout pages

**Day 3-4: Order Module**
- Order creation from invoices
- Payment success/failure handlers
- Order history pages

**Day 5-7: Stripe Webhooks**
- Webhook endpoints
- Background processors (15+ events)
- Test webhook flows

### Week 5: Subscriptions

**Day 1-2: Subscription Backend**
- Subscription CRUD
- Out-of-band subscription flow
- Price updates

**Day 3-4: Subscription Frontend**
- Subscription management UI
- Customer portal

**Day 5-7: Background Jobs**
- Subscription cycling
- Meter updates
- Webhook processing

### Week 6: AgentPay

**Day 1-2: Agent Backend**
- Orchestrator (6 layers)
- Claude integration
- Tool definitions

**Day 3-4: RAG System**
- pgvector setup
- Product embeddings
- Semantic search

**Day 5-7: Chat Frontend**
- Chat widget component
- SSE streaming
- Conversation UI

### Week 7-8: Polish & Deploy

**Day 1-2: Testing**
- Backend tests (pytest)
- Fix critical bugs

**Day 3-4: Production Prep**
- Environment variables
- Database migrations
- Monitoring setup

**Day 5-6: Deployment**
- Backend to DigitalOcean
- Frontend to Vercel
- Domain setup

**Day 7: Launch**
- Onboard first customer
- Monitor errors
- Celebrate 🎉

---

## Critical Implementation Notes

### 1. No Session.commit() in Business Logic

```python
# ❌ WRONG
async def create_product(session: AsyncSession, product_create: ProductCreate):
    product = Product(**product_create.dict())
    session.add(product)
    await session.commit()  # ❌ Never do this
    return product

# ✅ CORRECT
async def create_product(session: AsyncSession, product_create: ProductCreate):
    product = Product(**product_create.dict())
    session.add(product)
    # Middleware commits at end of request
    return product
```

**Why:** Ensures atomic transactions and consistent error handling.

### 2. Soft Deletion Pattern

```python
# All models have deleted_at
class Product(RecordModel):
    deleted_at: Mapped[datetime | None]

# Repository filters automatically
def get_base_statement(self) -> Select:
    return select(self.model).where(self.model.deleted_at.is_(None))
```

### 3. Stripe Idempotency Keys

```python
# Always use idempotency keys for Stripe
idempotency_key = f"freely:subscription:{subscription_id}"

await stripe_lib.Subscription.create_async(
    ...,
    idempotency_key=idempotency_key,
)
```

### 4. Webhook Event Queueing

```python
# Webhook endpoint: receive + validate + queue
@router.post("/webhook")
async def webhook(event: stripe.Event, session: AsyncSession):
    if event["type"] in IMPLEMENTED_WEBHOOKS:
        await enqueue_webhook(session, event)  # Queue to Dramatiq
    return 200  # Always return quickly

# Background worker: process
@actor(actor_name="stripe.webhook.charge.succeeded")
async def charge_succeeded(event_id: UUID):
    async with AsyncSessionMaker() as session:
        # Process event
        ...
```

### 5. Type Safety Everywhere

```python
# Backend: SQLAlchemy 2.0 with Mapped[]
class Product(RecordModel):
    name: Mapped[str]
    price: Mapped[int | None]

# Frontend: OpenAPI TypeScript
const { data } = await api.GET('/v1/products/{id}', {
  params: { path: { id: productId } }  // Type-safe
})
```

---

## UI/UX Replication Checklist

To achieve **identical** visual appearance to Polar:

### Colors
- ✅ Copy OKLCH blue/green/red/gray scales
- ✅ Copy Polar brand colors (HSL 233°)
- ✅ Copy semantic color mappings (light + dark)

### Typography
- ✅ Use Geist Sans + Geist Mono fonts
- ✅ Copy font-size scale
- ✅ Copy font-rendering settings

### Borders
- ✅ Base radius: 0.6rem
- ✅ Use rounded-xl (1.2rem) for buttons/inputs
- ✅ Use rounded-4xl (2rem) for cards
- ✅ Use rounded-full for pills

### Shadows
- ✅ Copy shadow-xs, shadow-md, shadow-lg definitions
- ✅ Apply shadows consistently (cards, dropdowns)

### Spacing
- ✅ Use Tailwind default spacing (0.25rem increments)
- ✅ Common: p-6, p-8, gap-4

### Components
- ✅ Implement all 26 Radix Vue components
- ✅ Implement all 32 custom atoms
- ✅ Match button variants exactly
- ✅ Match card patterns exactly
- ✅ Match input/form patterns exactly

### Dark Mode
- ✅ Class-based strategy (class="dark")
- ✅ Copy dark mode color mappings

---

## Dependencies

### Backend (pyproject.toml)

```toml
[project]
name = "freely"
version = "1.0.0"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.120.2",
    "uvicorn[standard]>=0.31.1",
    "pydantic>=2.11",
    "pydantic-settings>=2.5.2",
    "sqlalchemy[asyncio]>=2.0.34",
    "asyncpg>=0.29.0",
    "alembic>=1.9.2",
    "stripe>=10.12.0,<12",
    "dramatiq[redis]>=1.17.1",
    "apscheduler>=3.10.4",
    "redis>=5.0.4",
    "boto3>=1.38.30",
    "anthropic>=0.40.0",
    "sentry-sdk[fastapi,sqlalchemy]>=2.16.0",
    "structlog>=24.4.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "mypy>=1.11",
    "ruff>=0.6.9",
]
```

### Frontend (package.json)

```json
{
  "name": "freely-web",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "nuxt dev",
    "build": "nuxt build",
    "preview": "nuxt preview"
  },
  "dependencies": {
    "nuxt": "^3.15.0",
    "vue": "^3.5.0",
    "@nuxt/ui": "^3.5.0",
    "@radix-vue/nuxt": "^1.9.0",
    "@vueuse/core": "^11.0.0",
    "@vueuse/nuxt": "^11.0.0",
    "@vueuse/motion": "^2.2.0",
    "pinia": "^2.2.0",
    "@pinia/nuxt": "^0.8.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/typography": "^0.5.0",
    "@tailwindcss/forms": "^0.5.0",
    "openapi-typescript": "^7.0.0",
    "openapi-fetch": "^0.15.0"
  },
  "devDependencies": {
    "@nuxt/devtools": "latest",
    "typescript": "^5.7.0"
  }
}
```

---

## Deployment Strategy

### Backend (DigitalOcean App Platform)

```yaml
# .do/app.yaml
name: freely-backend
services:
  - name: api
    source:
      repo: muriloscigliano/flowpay
      branch: main
      source_dir: /server
    instance_size: basic-xs  # $12/mo
    http_port: 8000
    run_command: uv run uvicorn freely.app:app --host 0.0.0.0 --port 8000
    envs:
      - key: FREELY_ENV
        value: production
      - key: FREELY_DATABASE_URL
        scope: RUN_TIME
        type: SECRET

  - name: worker
    source:
      repo: muriloscigliano/flowpay
      branch: main
      source_dir: /server
    instance_size: basic-xs  # $12/mo
    run_command: uv run dramatiq freely.worker
    envs:
      - key: FREELY_ENV
        value: production

databases:
  - name: postgres
    engine: PG
    version: "16"
    production: true
    instance_size: db-basic-xs  # $15/mo

  - name: redis
    engine: REDIS
    version: "7"
    production: true
    instance_size: db-basic-xs  # $15/mo
```

**Total Backend Cost:** $54/mo

### Frontend (Vercel)

```bash
# vercel.json
{
  "framework": "nuxt",
  "buildCommand": "pnpm build",
  "outputDirectory": ".output/public",
  "installCommand": "pnpm install",
  "env": {
    "NUXT_PUBLIC_API_URL": "https://api.freely.you"
  }
}
```

**Cost:** Free tier (100GB bandwidth/mo)

---

## Success Criteria

### Week 2
- ✅ Can log in/out
- ✅ Dashboard loads with correct styling
- ✅ Dark mode works

### Week 4
- ✅ Can create product
- ✅ Product syncs to Stripe
- ✅ Can checkout and pay
- ✅ Order created successfully

### Week 6
- ✅ Recurring subscriptions work
- ✅ Customer can manage subscription
- ✅ AI chat responds to queries

### Week 8
- ✅ Deployed to production
- ✅ Domain working (freely.you)
- ✅ First customer onboarded
- ✅ No Polar attribution needed (built from scratch)

---

## Risk Mitigation

### Risk 1: Stripe Integration Complexity
**Mitigation:** Start with simple payment flow, add subscriptions later.

### Risk 2: Database Design Mistakes
**Mitigation:** Review Polar's schema thoroughly, use Alembic for easy migrations.

### Risk 3: Authentication Bugs
**Mitigation:** Copy Polar's AuthSubject pattern exactly, add tests early.

### Risk 4: Timeline Overrun
**Mitigation:** MVP first (products + checkout), add features incrementally.

### Risk 5: UI Not Matching
**Mitigation:** Copy globals.css exactly, use Polar as reference for every component.

---

## Next Steps

**Immediate (Today):**
1. ✅ Review this plan
2. ✅ Confirm tech stack decision (Nuxt)
3. ✅ Set up project structure (server/ + clients/)
4. ✅ Initialize Git repository (new, independent from Polar)

**Tomorrow:**
1. ✅ Backend: Install dependencies, create base models
2. ✅ Frontend: Nuxt setup, Tailwind configuration
3. ✅ Docker Compose: PostgreSQL + Redis

**This Week:**
1. ✅ Complete Phase 1 (Foundation)
2. ✅ Authentication working
3. ✅ Basic dashboard loading

---

**This plan builds Freely from scratch with NO Polar attribution required, while maintaining identical UI/UX.**

**Ready to start Week 1?**
