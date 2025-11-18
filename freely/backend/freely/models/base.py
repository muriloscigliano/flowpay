"""
Base models for Freely.

Implements the core model hierarchy:
- Model (DeclarativeBase)
- TimestampedModel (created_at, modified_at, deleted_at)
- IDModel (UUID primary key)
- RecordModel (combines ID + Timestamped)
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.utcnow()


class Model(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # Type annotations for mypy
    __name__: str
    __tablename__: str

    # Disable implicit table name generation
    __abstract__ = True


class TimestampedModel(Model):
    """Model with automatic timestamp tracking and soft deletion."""

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=utc_now,
        server_default=func.now(),
    )
    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        onupdate=utc_now,
        server_onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        default=None,
    )


class IDModel(Model):
    """Model with UUID primary key."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )


class RecordModel(IDModel, TimestampedModel):
    """
    Standard model combining ID and timestamps.

    This is what most models should inherit from.
    Provides:
    - UUID primary key (id)
    - Automatic timestamps (created_at, modified_at)
    - Soft deletion support (deleted_at)
    """

    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
