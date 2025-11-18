"""Database utilities."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from freely.config import settings

# Type aliases
AsyncSessionMaker = async_sessionmaker[AsyncSession]


def create_engine() -> AsyncEngine:
    """Create async database engine."""
    return create_async_engine(
        settings.get_postgres_dsn("asyncpg"),
        echo=settings.is_development,
        pool_size=5,
        pool_recycle=600,
    )


def create_sessionmaker(engine: AsyncEngine) -> AsyncSessionMaker:
    """Create async session maker."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


# Global instances (initialized in app lifespan)
_engine: AsyncEngine | None = None
_sessionmaker: AsyncSessionMaker | None = None


def get_engine() -> AsyncEngine:
    """Get global async engine."""
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    return _engine


def get_sessionmaker() -> AsyncSessionMaker:
    """Get global session maker."""
    if _sessionmaker is None:
        raise RuntimeError("Database session maker not initialized")
    return _sessionmaker


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.

    Usage:
        async with get_session() as session:
            # Use session
    """
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db(engine: AsyncEngine | None = None) -> None:
    """Initialize database (for testing)."""
    from freely.models import Model

    if engine is None:
        engine = get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def drop_db(engine: AsyncEngine | None = None) -> None:
    """Drop all tables (for testing)."""
    from freely.models import Model

    if engine is None:
        engine = get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


__all__ = [
    "AsyncSessionMaker",
    "create_engine",
    "create_sessionmaker",
    "get_engine",
    "get_sessionmaker",
    "get_session",
    "init_db",
    "drop_db",
]
