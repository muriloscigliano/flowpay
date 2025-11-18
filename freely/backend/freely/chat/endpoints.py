"""Chat endpoints - API for conversations and messages."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from freely.auth.dependencies import AuthenticatedUser, CurrentUser, get_db_session
from freely.chat.service import chat_service
from freely.models import User

router = APIRouter(prefix="/chat", tags=["chat"])


# Schemas
class ConversationCreate(BaseModel):
    """Create a new conversation."""

    customer_email: str | None = None
    customer_name: str | None = None
    organization_id: str | None = None


class MessageCreate(BaseModel):
    """Send a message."""

    content: str
    conversation_id: str | None = None  # If None, creates new conversation


class MessageResponse(BaseModel):
    """Message response."""

    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str

    @classmethod
    def from_message(cls, message) -> "MessageResponse":
        return cls(
            id=str(message.id),
            conversation_id=str(message.conversation_id),
            role=message.role,
            content=message.content,
            created_at=message.created_at.isoformat(),
        )


class ConversationResponse(BaseModel):
    """Conversation response."""

    id: str
    title: str | None
    customer_email: str | None
    customer_name: str | None
    created_at: str
    messages: list[MessageResponse]

    @classmethod
    def from_conversation(cls, conversation) -> "ConversationResponse":
        return cls(
            id=str(conversation.id),
            title=conversation.title,
            customer_email=conversation.customer_email,
            customer_name=conversation.customer_name,
            created_at=conversation.created_at.isoformat(),
            messages=[MessageResponse.from_message(m) for m in conversation.messages],
        )


# Endpoints
@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreate,
    auth_subject: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ConversationResponse:
    """Create a new conversation."""
    user = auth_subject.subject if not auth_subject.is_anonymous else None

    conversation = await chat_service.create_conversation(
        session,
        user=user,  # type: ignore
        organization_id=UUID(request.organization_id) if request.organization_id else None,
        customer_email=request.customer_email,
        customer_name=request.customer_name,
    )

    # Eager load messages (empty for new conversation)
    conversation.messages = []

    return ConversationResponse.from_conversation(conversation)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    auth_subject: AuthenticatedUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[ConversationResponse]:
    """List user's conversations."""
    conversations = await chat_service.list_conversations(session, auth_subject.subject)

    # Eager load messages for each conversation
    for conv in conversations:
        conv.messages = await chat_service.get_conversation_messages(session, conv.id)

    return [ConversationResponse.from_conversation(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    auth_subject: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ConversationResponse:
    """Get a conversation by ID."""
    user = auth_subject.subject if not auth_subject.is_anonymous else None

    conversation = await chat_service.get_conversation(
        session, conversation_id, user=user  # type: ignore
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Load messages
    conversation.messages = await chat_service.get_conversation_messages(session, conversation.id)

    return ConversationResponse.from_conversation(conversation)


@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: MessageCreate,
    auth_subject: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageResponse:
    """
    Send a message and get AI response.

    If conversation_id is provided, adds to existing conversation.
    If conversation_id is None, creates a new conversation.
    """
    user = auth_subject.subject if not auth_subject.is_anonymous else None

    # Get or create conversation
    if request.conversation_id:
        conversation = await chat_service.get_conversation(
            session, UUID(request.conversation_id), user=user  # type: ignore
        )
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation
        conversation = await chat_service.create_conversation(
            session,
            user=user,  # type: ignore
        )

    # Add user message
    user_message = await chat_service.add_message(
        session,
        conversation,
        role="user",
        content=request.content,
    )

    # Get previous messages for context
    previous_messages = await chat_service.get_conversation_messages(session, conversation.id)

    # Get AI response from agent
    from freely.agent import agent_service
    ai_response = await agent_service.process_message(
        conversation,
        previous_messages,
        request.content,
    )

    # Add AI message
    ai_message = await chat_service.add_message(
        session,
        conversation,
        role="assistant",
        content=ai_response,
    )

    return MessageResponse.from_message(ai_message)
