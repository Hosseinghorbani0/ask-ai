import asyncio
import threading
import time
from collections.abc import AsyncIterator, Iterator
from typing import Any, Optional

from .base import DEFAULT_RETRY_COUNT, Response


class ConversationSession:
    """In-memory conversation state backed by an existing provider."""

    def __init__(
        self,
        provider: Any,
        max_messages: Optional[int] = None,
        strict_options: bool = False,
    ):
        self.provider = provider
        self.max_messages = max_messages
        self.strict_options = strict_options
        self.messages: list[dict[str, str]] = []
        self._sync_lock = threading.RLock()
        self._async_lock = asyncio.Lock()

    def _trim(self) -> None:
        if self.max_messages is None or self.max_messages <= 0:
            return
        max_pair_messages = self.max_messages - (self.max_messages % 2)
        while len(self.messages) > max_pair_messages:
            del self.messages[:2]

    def clear(self) -> None:
        with self._sync_lock:
            self.messages.clear()

    def _validate_options(self, kwargs: dict[str, Any], streaming: bool = False) -> None:
        if streaming and kwargs.get("response_model") is not None:
            raise NotImplementedError(
                "Structured response validation is not supported for streaming sessions."
            )
        if self.strict_options and "strict_options" not in kwargs:
            kwargs["strict_options"] = True

    def _messages_for_request(self, query: str, config: Any) -> list[dict[str, str]]:
        request_messages = self.provider._prepare_messages(query, config)
        if request_messages and request_messages[0]["role"] == "system":
            return [request_messages[0], *self.messages, request_messages[-1]]
        return [*self.messages, *request_messages]

    def ask(self, query: str, **kwargs: Any):
        with self._sync_lock:
            return self._ask_locked(query, kwargs)

    def _ask_locked(self, query: str, kwargs: dict[str, Any]):
        self._validate_options(kwargs)
        started_at = time.perf_counter()
        config = self.provider._build_final_config(kwargs)
        messages = self._messages_for_request(query, config)
        response = self.provider._execute_response(
            messages,
            config,
            kwargs.get("output_type"),
            int(
                kwargs.get("retry", config.extra.get("retry", DEFAULT_RETRY_COUNT))
                or 0
            ),
            kwargs.get("response_model"),
            int(kwargs.get("validation_retries", 0) or 0),
            started_at,
        )
        self.messages.extend(
            [{"role": "user", "content": query}, {"role": "assistant", "content": response.text}]
        )
        self._trim()
        return response

    async def ask_async(self, query: str, **kwargs: Any):
        async with self._async_lock:
            return await self._ask_async_locked(query, kwargs)

    async def _ask_async_locked(self, query: str, kwargs: dict[str, Any]):
        self._validate_options(kwargs)
        started_at = time.perf_counter()
        config = self.provider._build_final_config(kwargs)
        messages = self._messages_for_request(query, config)
        response = await self.provider._execute_response_async(
            messages,
            config,
            kwargs.get("output_type"),
            int(
                kwargs.get("retry", config.extra.get("retry", DEFAULT_RETRY_COUNT))
                or 0
            ),
            kwargs.get("response_model"),
            int(kwargs.get("validation_retries", 0) or 0),
            started_at,
        )
        self.messages.extend(
            [{"role": "user", "content": query}, {"role": "assistant", "content": response.text}]
        )
        self._trim()
        return response

    def ask_stream(self, query: str, **kwargs: Any) -> Iterator[str]:
        with self._sync_lock:
            self._validate_options(kwargs, streaming=True)
            started_at = time.perf_counter()
            config = self.provider._build_final_config(kwargs)
            messages = self._messages_for_request(query, config)
            retry = int(
                kwargs.get("retry", config.extra.get("retry", DEFAULT_RETRY_COUNT)) or 0
            )
            chunks = []
            for chunk in self.provider._iter_with_retry(
                lambda: self.provider._send_request_stream(messages, config),
                retry,
                deadline=self.provider._create_deadline(config),
                config=config,
            ):
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
        async with self._async_lock:
            self._validate_options(kwargs, streaming=True)
            started_at = time.perf_counter()
            config = self.provider._build_final_config(kwargs)
            messages = self._messages_for_request(query, config)
            retry = int(
                kwargs.get("retry", config.extra.get("retry", DEFAULT_RETRY_COUNT)) or 0
            )
            chunks = []
            async for chunk in self.provider._aiter_with_retry(
                lambda: self.provider._send_request_stream_async(messages, config),
                retry,
                deadline=self.provider._create_deadline(config),
                config=config,
            ):
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
