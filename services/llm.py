"""LLM utilities and clients for simulator/evaluator orchestration."""
from __future__ import annotations

from typing import Any, Optional, Protocol

from core.config import Settings


class LLMClientProtocol(Protocol):
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        ...


class NoopLLMClient:
    """Fallback client that simply echoes prompts for deterministic dry-runs."""

    async def generate(self, prompt: str, **kwargs: Any) -> str:  # pragma: no cover - trivial
        return prompt


class OpenAIChatClient:
    """Thin wrapper around the async OpenAI Chat Completions API."""

    def __init__(self, api_key: str, model: str, temperature: float) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self._client: Optional["AsyncOpenAI"] = None

    async def _get_client(self) -> "AsyncOpenAI":
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as exc:  # pragma: no cover - optional dep
                raise RuntimeError(
                    "openai package is required. Install via `pip install openai`."
                ) from exc
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        client = await self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            temperature=kwargs.get("temperature", self.temperature),
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content or ""
        return content.strip()


class AnthropicMessagesClient:
    """Wrapper around Anthropic Messages API."""

    def __init__(self, api_key: str, model: str, temperature: float) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self._client: Optional["AsyncAnthropic"] = None

    async def _get_client(self) -> "AsyncAnthropic":
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
            except ImportError as exc:  # pragma: no cover - optional dep
                raise RuntimeError(
                    "anthropic package is required. Install via `pip install anthropic`."
                ) from exc
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        client = await self._get_client()
        response = await client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 512),
            temperature=kwargs.get("temperature", self.temperature),
            messages=[{"role": "user", "content": prompt}],
        )
        chunks = []
        for block in response.content:
            if block.type == "text":
                chunks.append(block.text)
        return " ".join(chunks).strip()


def build_llm_client(settings: Settings) -> LLMClientProtocol:
    """Return the most capable configured LLM client, defaulting to noop."""

    if settings.openai_api_key:
        return OpenAIChatClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.llm_temperature,
        )
    if settings.anthropic_api_key:
        return AnthropicMessagesClient(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            temperature=settings.llm_temperature,
        )
    return NoopLLMClient()
