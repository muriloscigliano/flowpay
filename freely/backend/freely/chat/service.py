"""Chat service - Business logic for conversations and messages."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from freely.models import Conversation, Message, User


class ChatService:
    """Service for managing chat conversations and messages."""

    @staticmethod
    async def create_conversation(
        session: AsyncSession,
        user: User | None = None,
        organization_id: UUID | None = None,
        customer_email: str | None = None,
        customer_name: str | None = None,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=user.id if user else None,
            organization_id=organization_id,
            customer_email=customer_email,
            customer_name=customer_name,
        )

        session.add(conversation)
        await session.flush()

        return conversation

    @staticmethod
    async def get_conversation(
        session: AsyncSession,
        conversation_id: UUID,
        user: User | None = None,
    ) -> Conversation | None:
        """Get conversation by ID with authorization check."""
        stmt = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.deleted_at.is_(None),
            )
            .options(selectinload(Conversation.messages))
        )

        # Authorization: user can only access their own conversations
        if user:
            stmt = stmt.where(Conversation.user_id == user.id)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_conversations(
        session: AsyncSession,
        user: User,
        limit: int = 50,
    ) -> list[Conversation]:
        """List user's conversations."""
        stmt = (
            select(Conversation)
            .where(
                Conversation.user_id == user.id,
                Conversation.deleted_at.is_(None),
            )
            .order_by(Conversation.created_at.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def add_message(
        session: AsyncSession,
        conversation: Conversation,
        role: str,
        content: str,
        metadata_json: str | None = None,
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            metadata_json=metadata_json,
        )

        session.add(message)
        await session.flush()

        return message

    @staticmethod
    async def get_conversation_messages(
        session: AsyncSession,
        conversation_id: UUID,
    ) -> list[Message]:
        """Get all messages for a conversation."""
        stmt = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.deleted_at.is_(None),
            )
            .order_by(Message.created_at.asc())
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())


# Singleton instance
chat_service = ChatService()
