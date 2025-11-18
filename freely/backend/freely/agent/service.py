"""Agent service - Orchestrates AI conversations."""

import json
from typing import AsyncGenerator

from freely.agent.claude import claude_client
from freely.models import Conversation, Message


class AgentService:
    """Service for AI agent interactions."""

    async def process_message(
        self,
        conversation: Conversation,
        messages: list[Message],
        user_message: str,
    ) -> str:
        """
        Process a user message and generate AI response.

        Args:
            conversation: Current conversation
            messages: Previous messages in conversation
            user_message: New message from user

        Returns:
            AI response text
        """
        # Build message history for Claude
        claude_messages = self._build_message_history(messages, user_message)

        # Get AI response
        response = await claude_client.chat(claude_messages)

        return response

    async def process_message_stream(
        self,
        conversation: Conversation,
        messages: list[Message],
        user_message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI response.

        Args:
            conversation: Current conversation
            messages: Previous messages in conversation
            user_message: New message from user

        Yields:
            Text chunks from AI
        """
        # Build message history for Claude
        claude_messages = self._build_message_history(messages, user_message)

        # Stream AI response
        async for chunk in claude_client.chat_stream(claude_messages):
            yield chunk

    def _build_message_history(
        self,
        messages: list[Message],
        new_message: str,
    ) -> list[dict[str, str]]:
        """
        Build message history for Claude API.

        Claude expects: [{"role": "user", "content": "..."}, ...]
        """
        claude_messages = []

        # Add previous messages
        for msg in messages:
            if msg.role in ["user", "assistant"]:
                claude_messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                    }
                )

        # Add new user message
        claude_messages.append(
            {
                "role": "user",
                "content": new_message,
            }
        )

        return claude_messages


# Singleton instance
agent_service = AgentService()
