"""Freely configuration using Pydantic Settings."""

from enum import Enum
from typing import Literal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings.

    All environment variables are prefixed with FREELY_
    Example: FREELY_ENV=production
    """

    model_config = SettingsConfigDict(
        env_prefix="FREELY_",
        env_file=".env",
        case_sensitive=False,
    )

    # Environment
    ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BASE_URL: str = "http://127.0.0.1:8000"
    FRONTEND_BASE_URL: str = "http://127.0.0.1:3000"

    # Database
    POSTGRES_USER: str = "freely"
    POSTGRES_PASSWORD: str = "freely"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str = "freely_development"

    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Security
    SECRET_KEY: str = "super-secret-key-change-in-production"
    SESSION_TTL_DAYS: int = 30

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_CONNECT_WEBHOOK_SECRET: str = ""

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # AWS S3 / MinIO
    AWS_ACCESS_KEY_ID: str = "freely-development"
    AWS_SECRET_ACCESS_KEY: str = "freely123456789"
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str | None = "http://localhost:9000"  # MinIO in dev
    S3_BUCKET_NAME: str = "freely-uploads"

    # Sentry
    SENTRY_DSN: str | None = None

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Properties
    @property
    def is_development(self) -> bool:
        return self.ENV == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.ENV == Environment.TESTING

    @property
    def is_production(self) -> bool:
        return self.ENV == Environment.PRODUCTION

    def get_postgres_dsn(self, driver: Literal["asyncpg", "psycopg2"] = "asyncpg") -> str:
        """Get PostgreSQL DSN for SQLAlchemy."""
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{driver}",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DATABASE,
            )
        )

    def get_redis_url(self) -> str:
        """Get Redis URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Global settings instance
settings = Settings()
