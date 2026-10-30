import time
from collections.abc import AsyncIterator, Iterator
from typing import Any, Optional

from .base import Response


class ConversationSession:
    """In-memory conversation state backed by an existing provider."""

    def __init__(self, provider: Any, max_messages: Optional[int] = None):
        self.provider = provider
        self.max_messages = max_messages
        self.messages: list[dict[str, str]] = []

    def _trim(self) -> None:
        if self.max_messages is None or self.max_messages <= 0:
            return
        max_pair_messages = self.max_messages - (self.max_messages % 2)
        while len(self.messages) > max_pair_messages:
            del self.messages[:2]

    def clear(self) -> None:
        self.messages.clear()

    def ask(self, query: str, **kwargs: Any):
        started_at = time.perf_counter()
        config = self.provider._build_final_config(kwargs)
        messages = [*self.messages, {"role": "user", "content": query}]
        response = self.provider._execute_with_retry(
            self.provider._send_request,
            messages,
            config,
            kwargs.get("output_type"),
            int(kwargs.get("retry", config.extra.get("retry", 0)) or 0),
        )
        response = self.provider._attach_metadata(
            response,
            started_at,
            getattr(self.provider, "_retry_count", 0),
        )
        self.messages.extend(
            [{"role": "user", "content": query}, {"role": "assistant", "content": response.text}]
        )
        self._trim()
        return response

    async def ask_async(self, query: str, **kwargs: Any):
        started_at = time.perf_counter()
        config = self.provider._build_final_config(kwargs)
        messages = [*self.messages, {"role": "user", "content": query}]
        response = await self.provider._execute_with_retry_async(
            self.provider._send_request_async,
            messages,
            config,
            kwargs.get("output_type"),
            int(kwargs.get("retry", config.extra.get("retry", 0)) or 0),
        )
        response = self.provider._attach_metadata(
            response,
            started_at,
            getattr(self.provider, "_retry_count", 0),
        )
        self.messages.extend(
            [{"role": "user", "content": query}, {"role": "assistant", "content": response.text}]
        )
        self._trim()
        return response

    def ask_stream(self, query: str, **kwargs: Any) -> Iterator[str]:
        started_at = time.perf_counter()
        config = self.provider._build_final_config(kwargs)
        messages = [*self.messages, {"role": "user", "content": query}]
        chunks = []
        for chunk in self.provider._send_request_stream(messages, config):
            chunks.append(chunk)
            yield chunk
        self.messages.extend(
            [{"role": "user", "content": query}, {"role": "assistant", "content": "".join(chunks)}]
        )
        self.provider._attach_metadata(
            Response(text="".join(chunks)),
            started_at,
            getattr(self.provider, "_retry_count", 0),
        )
        self._trim()

    async def ask_stream_async(self, query: str, **kwargs: Any) -> AsyncIterator[str]:
        started_at = time.perf_counter()
        config = self.provider._build_final_config(kwargs)
        messages = [*self.messages, {"role": "user", "content": query}]
        chunks = []
        async for chunk in self.provider._send_request_stream_async(messages, config):
            chunks.append(chunk)
            yield chunk
        self.messages.extend(
            [{"role": "user", "content": query}, {"role": "assistant", "content": "".join(chunks)}]
        )
        self.provider._attach_metadata(
            Response(text="".join(chunks)),
            started_at,
            getattr(self.provider, "_retry_count", 0),
        )
        self._trim()
