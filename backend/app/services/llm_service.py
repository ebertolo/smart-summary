"""
LLM Service with LangChain integration
Supports Anthropic Claude models only
"""

import asyncio
from typing import AsyncGenerator, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings


class LLMService:
    """
    LLM service abstraction using LangChain
    Supports Anthropic Claude models only
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = True,
    ):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.streaming = streaming

        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize LLM - only Anthropic Claude supported"""
        if self.provider == "anthropic":
            return ChatAnthropic(
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming,
            )
        else:
            raise ValueError(
                f"Only 'anthropic' provider is supported. Got: {self.provider}"
            )

    async def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generate completion (non-streaming)"""
        messages = []

        if system_message:
            messages.append(SystemMessage(content=system_message))

        messages.append(HumanMessage(content=prompt))

        response = await self.llm.ainvoke(messages)
        return response.content

    async def generate_stream(
        self, prompt: str, system_message: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate completion with streaming"""
        messages = []

        if system_message:
            messages.append(SystemMessage(content=system_message))

        messages.append(HumanMessage(content=prompt))

        print(f"[LLM] Calling Claude - model: {self.model}")

        try:
            print(f"[LLM] Stream started")
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
        except asyncio.CancelledError:
            # Request was cancelled (client disconnected)
            # Just cleanup and exit gracefully
            raise  # Re-raise to properly propagate cancellation

    def create_prompt_template(self, template: str) -> ChatPromptTemplate:
        """Create a chat prompt template"""
        return ChatPromptTemplate.from_template(template)
