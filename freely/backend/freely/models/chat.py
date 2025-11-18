"""Chat models - Conversations and Messages."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from freely.models.base import RecordModel

if TYPE_CHECKING:
    from freely.models import Organization, User


class Conversation(RecordModel):
    """
    Chat conversation.

    Can be:
    - Anonymous chat (no user_id)
    - Authenticated user chat (has user_id)
    - Organization-scoped (has organization_id for multi-tenant)
    """

    __tablename__ = "conversations"

    # Customer info
    customer_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # User (if authenticated)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Organization (for multi-tenant)
    organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )

    # Conversation metadata
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Relationships
    user: Mapped["User | None"] = relationship("User", lazy="joined")
    organization: Mapped["Organization | None"] = relationship("Organization", lazy="joined")
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        lazy="raise",
        order_by="Message.created_at",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} title={self.title}>"


class Message(RecordModel):
    """
    Chat message.

    Role can be:
    - 'user': Message from the customer
    - 'assistant': Message from AI
    - 'system': System messages (optional)
    """

    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' | 'assistant' | 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata (for tracking tokens, model used, etc.)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message id={self.id} role={self.role} content={preview}>"
