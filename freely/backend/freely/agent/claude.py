"""Claude AI integration using Anthropic API."""

import json
from typing import AsyncGenerator

from anthropic import AsyncAnthropic

from freely.config import settings


class ClaudeClient:
    """Client for interacting with Claude AI via Anthropic API."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send messages to Claude and get response.

        Args:
            messages: List of {role: "user"|"assistant", content: "..."}
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response

        Returns:
            AI response text
        """
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt or self._get_default_system_prompt(),
            messages=messages,
        )

        # Extract text from response
        if response.content and len(response.content) > 0:
            return response.content[0].text

        return "I apologize, I couldn't generate a response."

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """
        Stream Claude's response.

        Yields:
            Text chunks as they arrive
        """
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt or self._get_default_system_prompt(),
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for AI assistant."""
        return """You are Freely AI, a helpful conversational commerce assistant.

Your role is to:
- Help customers find and purchase products
- Answer questions about products and services
- Provide excellent customer service
- Be friendly, professional, and concise

Keep responses helpful and conversational. If you don't know something, say so."""


# Singleton instance
claude_client = ClaudeClient()
