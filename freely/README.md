# Freely - Conversational Commerce Platform

Built from scratch with AI-powered chat capabilities. Features authentication, AI chat with Claude, and a clean modern UI inspired by Polar's design system.

## Architecture

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL 16 + pgvector
- **Cache/Queue**: Redis 7
- **Storage**: MinIO (S3-compatible)
- **AI**: Anthropic Claude 3.5 Sonnet
- **Package Manager**: uv

### Frontend
- **Framework**: Nuxt 4 + Vue 3.5
- **Styling**: Tailwind CSS v4 with OKLCH colors
- **State**: Pinia + VueUse composables
- **Package Manager**: pnpm

## Quick Start

### Backend Setup

1. **Install uv** (Python package manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Start infrastructure services**
```bash
cd freely/backend
docker compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (ports 9000, 9001)

3. **Configure environment**
```bash
cd freely/backend
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
FREELY_ANTHROPIC_API_KEY=sk-ant-...
FREELY_SECRET_KEY=your-secret-key-here
```

4. **Install dependencies**
```bash
cd freely/backend
uv sync
```

5. **Run database migrations**
```bash
cd freely/backend
uv run alembic upgrade head
```

6. **Start the API server**
```bash
cd freely/backend
uv run uvicorn freely.app:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://127.0.0.1:8000

### Frontend Setup

1. **Install pnpm** (if not installed)
```bash
curl -fsSL https://get.pnpm.io/install.sh | sh
```

2. **Install dependencies**
```bash
cd freely/frontend
pnpm install
```

3. **Configure environment** (optional)
```bash
cd freely/frontend
cp .env.example .env
```

The frontend defaults to `http://127.0.0.1:8000` for the API.

4. **Start development server**
```bash
cd freely/frontend
pnpm dev
```

Frontend will be available at: http://localhost:3000

## Features

### Implemented ✅

**Backend:**
- ✅ User authentication (register, login, logout, sessions)
- ✅ Bcrypt password hashing
- ✅ Session-based auth with HTTP-only cookies
- ✅ Organization multi-tenancy
- ✅ AI chat with Claude 3.5 Sonnet
- ✅ Conversation history management
- ✅ Message persistence
- ✅ Product catalog (CRUD operations)
- ✅ Category management
- ✅ Product search and filtering
- ✅ Pagination support
- ✅ Shopping cart (session-based and user-based)
- ✅ Cart item management (add, update, remove)
- ✅ Order creation from cart
- ✅ Stripe PaymentIntent integration
- ✅ Order management and history
- ✅ Price snapshots in cart/orders
- ✅ Async SQLAlchemy 2.0
- ✅ Alembic migrations
- ✅ RESTful API with FastAPI

**Frontend:**
- ✅ Modern UI with Polar's OKLCH color system
- ✅ Dark mode support
- ✅ Login/Register pages
- ✅ Chat interface with AI
- ✅ Real-time message UI
- ✅ Products listing page with grid view
- ✅ Product creation form
- ✅ Search and category filtering
- ✅ Pagination controls
- ✅ Shopping cart page
- ✅ Cart management (view, update quantities, remove)
- ✅ Cart state management with composables
- ✅ Customer order portal (order history)
- ✅ Order detail page with full information
- ✅ Order status displays (payment, fulfillment)
- ✅ useOrders composable for order management
- ✅ Auth state management
- ✅ Protected routes
- ✅ Responsive design

### Roadmap 🚧

**Future Enhancements:**
- Stripe Elements payment form frontend
- Order confirmation page after checkout
- Email notifications for orders
- Admin order fulfillment dashboard
- Webhook handling for payment events
- Subscriptions

**Week 5:**
- Analytics dashboard
- Reporting
- Admin panel

## Project Structure

```
freely/
├── backend/
│   ├── freely/
│   │   ├── auth/           # Authentication module
│   │   │   ├── endpoints.py    # Auth API routes
│   │   │   ├── service.py      # Auth business logic
│   │   │   ├── dependencies.py # Auth dependencies
│   │   │   └── models.py       # AuthSubject pattern
│   │   ├── chat/           # Chat module
│   │   │   ├── endpoints.py    # Chat API routes
│   │   │   └── service.py      # Chat business logic
│   │   ├── agent/          # AI agent module
│   │   │   ├── claude.py       # Claude API client
│   │   │   └── service.py      # Agent orchestration
│   │   ├── product/        # Product catalog module
│   │   │   ├── endpoints.py    # Product & Category routes
│   │   │   ├── service.py      # Product business logic
│   │   │   └── schemas.py      # Pydantic models
│   │   ├── models/         # Database models
│   │   │   ├── base.py         # Base model classes
│   │   │   ├── user.py         # User & UserSession
│   │   │   ├── organization.py # Organization
│   │   │   ├── chat.py         # Conversation & Message
│   │   │   └── product.py      # Product & Category
│   │   ├── kit/            # Utilities
│   │   │   ├── db.py           # Database utilities
│   │   │   └── crypto.py       # Password/token hashing
│   │   ├── api.py          # API router aggregation
│   │   ├── app.py          # FastAPI app factory
│   │   └── config.py       # Pydantic settings
│   ├── migrations/         # Alembic migrations
│   ├── docker-compose.yml  # Infrastructure services
│   └── pyproject.toml      # Python dependencies
│
└── frontend/
    ├── app/
    │   ├── pages/
    │   │   ├── index.vue       # Home page (redirects)
    │   │   ├── login.vue       # Login page
    │   │   ├── register.vue    # Register page
    │   │   ├── chat.vue        # Chat interface
    │   │   └── products/
    │   │       ├── index.vue   # Products listing
    │   │       └── new.vue     # Create product form
    │   └── middleware/
    │       └── auth.ts         # Auth middleware
    ├── composables/
    │   ├── useAuth.ts          # Auth state management
    │   ├── useChat.ts          # Chat state management
    │   └── useProducts.ts      # Product catalog management
    ├── assets/
    │   └── styles/
    │       └── globals.css     # OKLCH color system
    ├── nuxt.config.ts          # Nuxt configuration
    ├── tailwind.config.ts      # Tailwind config
    └── package.json            # Frontend dependencies
```

## API Endpoints

### Authentication

- `POST /v1/auth/register` - Create new user account
- `POST /v1/auth/login` - Login with email/password
- `POST /v1/auth/logout` - Logout current session
- `GET /v1/auth/me` - Get current authenticated user

### Chat

- `POST /v1/chat/conversations` - Create new conversation
- `GET /v1/chat/conversations` - List user's conversations
- `GET /v1/chat/conversations/{id}` - Get conversation by ID
- `POST /v1/chat/send` - Send message and get AI response

### Products

- `POST /v1/products` - Create new product
- `GET /v1/products` - List products (with pagination, search, filtering)
- `GET /v1/products/{id}` - Get product by ID
- `PATCH /v1/products/{id}` - Update product
- `DELETE /v1/products/{id}` - Delete product (soft delete)

### Categories

- `POST /v1/products/categories` - Create new category
- `GET /v1/products/categories` - List all categories
- `GET /v1/products/categories/{id}` - Get category by ID
- `PATCH /v1/products/categories/{id}` - Update category
- `DELETE /v1/products/categories/{id}` - Delete category (soft delete)

## Database Schema

### users
- `id` (UUID, PK)
- `email` (unique, indexed)
- `username` (unique, indexed)
- `password_hash` (bcrypt)
- `email_verified` (boolean)
- `avatar_url` (string)
- `is_admin` (boolean)
- `created_at`, `modified_at`, `deleted_at` (soft deletion)

### user_sessions
- `id` (UUID, PK)
- `token_hash` (SHA-256, unique, indexed)
- `expires_at` (ISO datetime)
- `user_id` (FK → users)
- `created_at`, `modified_at`, `deleted_at`

### organizations
- `id` (UUID, PK)
- `name`, `slug` (unique, indexed)
- `avatar_url`, `email`, `website`, `bio`
- `stripe_account_id` (unique, for Stripe Connect)
- `is_active`, `onboarded_at`
- `created_at`, `modified_at`, `deleted_at`

### conversations
- `id` (UUID, PK)
- `title` (auto-generated from first message)
- `customer_email`, `customer_name` (optional)
- `user_id` (FK → users, nullable for anonymous)
- `organization_id` (FK → organizations, multi-tenant)
- `created_at`, `modified_at`, `deleted_at`

### messages
- `id` (UUID, PK)
- `conversation_id` (FK → conversations)
- `role` ('user' | 'assistant' | 'system')
- `content` (text)
- `metadata_json` (optional JSON data)
- `created_at`, `modified_at`, `deleted_at`

### categories
- `id` (UUID, PK)
- `name`, `slug` (indexed)
- `description` (text, optional)
- `organization_id` (FK → organizations)
- `created_at`, `modified_at`, `deleted_at`

### products
- `id` (UUID, PK)
- `name`, `slug` (indexed)
- `description` (text, optional)
- `price_cents` (integer, stored in cents)
- `currency` (3-char ISO 4217, default: USD)
- `image_urls` (array of strings)
- `stock_available` (integer, nullable for unlimited)
- `is_available` (boolean, for sale status)
- `is_digital` (boolean, digital vs physical)
- `organization_id` (FK → organizations)
- `created_at`, `modified_at`, `deleted_at`

### product_categories
- `product_id` (FK → products)
- `category_id` (FK → categories)
- Composite PK (product_id, category_id)

## Design System

### Colors (OKLCH Format)

**Primary (Blue):**
- blue-600: `oklch(0.546 0.245 262.881)` - Primary buttons, links
- blue-500: `oklch(0.623 0.214 259.815)`

**Neutrals (Gray):**
- gray-50: `oklch(0.985 0.002 247.839)` - Background
- gray-900: `oklch(0.21 0.034 264.665)` - Text

**Semantic:**
- `--background`: gray-50 (light) / hsl(233, 5%, 9.5%) (dark)
- `--primary`: blue-600
- `--border`: gray-200
- `--radius`: 0.6rem (standard), 2rem (rounded-4xl for cards)

### Typography
- Font: System font stack
- Font features: `rlig`, `calt` (ligatures)

## Development

### Backend Commands

```bash
# Run API server
uv run uvicorn freely.app:app --reload

# Run tests
uv run pytest

# Type checking
uv run mypy freely

# Linting
uv run ruff check freely
uv run ruff format freely

# Create migration
uv run alembic revision --autogenerate -m "description"

# Run migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

### Frontend Commands

```bash
# Development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Type checking
pnpm typecheck

# Linting
pnpm lint
```

## Environment Variables

### Backend (.env)

```env
# Environment
FREELY_ENV=development

# Database
FREELY_POSTGRES_USER=freely
FREELY_POSTGRES_PASSWORD=freely
FREELY_POSTGRES_DATABASE=freely_development
FREELY_POSTGRES_HOST=127.0.0.1
FREELY_POSTGRES_PORT=5432

# Redis
FREELY_REDIS_HOST=127.0.0.1
FREELY_REDIS_PORT=6379

# MinIO (S3)
FREELY_MINIO_HOST=127.0.0.1
FREELY_MINIO_PORT=9000
FREELY_MINIO_ACCESS_KEY=freely
FREELY_MINIO_SECRET_KEY=freelysecret

# Security
FREELY_SECRET_KEY=your-secret-key-here-change-in-production
FREELY_SESSION_TTL_DAYS=30

# Anthropic AI
FREELY_ANTHROPIC_API_KEY=sk-ant-...
FREELY_ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Stripe (future)
FREELY_STRIPE_SECRET_KEY=
FREELY_STRIPE_PUBLISHABLE_KEY=
FREELY_STRIPE_WEBHOOK_SECRET=
```

### Frontend (.env)

```env
NUXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Testing the Complete Flow

1. **Start backend** (with Docker services running)
2. **Start frontend**
3. **Navigate to** http://localhost:3000
4. **Register** a new account
5. **Chat** with the AI assistant

The AI will:
- Remember conversation context
- Provide helpful responses
- Act as a conversational commerce assistant

## License

This project is built independently and does not use Polar's source code.

## Credits

- UI/UX design system inspired by [Polar](https://polar.sh)
- Built with Claude Code (Anthropic)
