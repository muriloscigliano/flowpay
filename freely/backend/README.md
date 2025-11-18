# Freely Backend

Python/FastAPI backend for Freely - Global commerce platform with AI agents.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- Docker & Docker Compose (for local services)

### Installation

```bash
# Install dependencies
uv sync

# Copy environment variables
cp .env.example .env

# Start local services (PostgreSQL, Redis, MinIO)
docker compose up -d

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn freely.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://127.0.0.1:8000

- API Docs: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/healthz

## Project Structure

```
freely/
├── models/          # SQLAlchemy models
│   ├── base.py     # Base model classes
│   ├── user.py
│   └── organization.py
├── auth/            # Authentication system
├── kit/             # Shared utilities
│   └── db/         # Database utilities
├── config.py        # Settings (Pydantic)
├── app.py           # FastAPI app factory
└── api.py           # Router aggregation

migrations/          # Alembic migrations
tests/               # Pytest tests
```

## Development

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=freely --cov-report=html

# Run specific test file
uv run pytest tests/test_models.py
```

### Linting

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check --fix .

# Type check
uv run mypy freely
```

## Environment Variables

All environment variables are prefixed with `FREELY_`. See `.env.example` for full list.

Key variables:
- `FREELY_ENV` - Environment (development, testing, production)
- `FREELY_POSTGRES_*` - PostgreSQL connection
- `FREELY_REDIS_*` - Redis connection
- `FREELY_STRIPE_SECRET_KEY` - Stripe API key
- `FREELY_ANTHROPIC_API_KEY` - Claude API key

## Architecture

### Models

All models inherit from `RecordModel` which provides:
- UUID primary key (`id`)
- Automatic timestamps (`created_at`, `modified_at`)
- Soft deletion support (`deleted_at`)

### Database

- **PostgreSQL 16** with pgvector extension
- **SQLAlchemy 2.0** with async support
- **Alembic** for migrations
- Automatic session management via middleware

### API

- **FastAPI** for async Python web framework
- **Pydantic** for request/response validation
- OpenAPI/Swagger docs auto-generated
- CORS middleware for frontend integration

### Background Jobs

- **Dramatiq** for async job processing
- **Redis** as message broker
- **APScheduler** for cron jobs

## License

Proprietary - Freely Team
