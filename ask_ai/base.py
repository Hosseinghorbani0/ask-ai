import asyncio
import logging
import math
import os
import random
import threading
import time
import weakref
from collections.abc import AsyncIterator, Iterator
from concurrent.futures import CancelledError as FutureCancelledError
from concurrent.futures import TimeoutError as FutureTimeoutError
from contextvars import ContextVar
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Optional, Union

from .capabilities import Capabilities
from .config import CONFIG_OPTION_NAMES, AdvancedConfig, validate_option_names
from .events import Completed, Error, TextDelta, ToolCall, UsageUpdate
from .exceptions import (
    MediaTypeNotSupportedError,
    ProviderError,
    ProviderTimeoutError,
    StructuredValidationError,
    safe_provider_error_label,
)
from .media import AudioObject, ImageObject
from .observability import Observability, ResponseMetadata, Usage

logger = logging.getLogger("ask_ai")
DEFAULT_RETRY_COUNT = 2
MAX_RETRY_DELAY = 30.0
JSONValue = Union[
    None,
    bool,
    int,
    float,
    str,
    list["JSONValue"],
    dict[str, "JSONValue"],
]


def _retry_after_seconds(error: Exception) -> Optional[float]:
    retry_after = getattr(error, "retry_after", None)
    if retry_after is None:
        response = getattr(error, "response", None)
        headers = getattr(response, "headers", None)
        if headers is not None:
            retry_after = headers.get("Retry-After")
    if retry_after is None:
        return None
    try:
        seconds = float(retry_after)
    except (TypeError, ValueError):
        try:
            retry_at = parsedate_to_datetime(str(retry_after))
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            seconds = (retry_at - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError, OverflowError):
            return None
    return min(MAX_RETRY_DELAY, max(0.0, seconds))


def _retry_delay(error: Exception, attempts: int) -> float:
    exponential = min(2**attempts + random.uniform(0, 1), MAX_RETRY_DELAY)
    retry_after = _retry_after_seconds(error)
    return min(MAX_RETRY_DELAY, max(exponential, retry_after or 0.0))


class Response:
    """
    Unified response object for all ask-ai requests.
    """
    def __init__(
        self,
        text: str = "",
        media: Union[ImageObject, AudioObject, None] = None,
        response_model: Any = None,
        metadata: Any = None,
        usage: Optional[Usage] = None,
        **kwargs,
    ):
        self._raw_text = text
        self.media = media
        self.response_model = response_model
        self.metadata = metadata
        self.usage = usage
        self._kwargs = kwargs

    @property
    def text(self) -> str:
        text = self._raw_text
        if self._kwargs.get('strip'):
            from .utils import strip_tags
            text = strip_tags(text)
        if self._kwargs.get('clean'):
            from .utils import clean_markdown
            text = clean_markdown(text)
        if self._kwargs.get('code'):
            from .utils import extract_code
            text = extract_code(text)
        return text

    @property
    def raw(self) -> str:
        """Return the unmodified provider text."""
        return self._raw_text

    @property
    def parsed(self) -> Any:
        """Return the validated structured response, if one was requested."""
        if self.response_model is None:
            raise ValueError("No response_model was specified for this request.")
        from .structured import parse_structured
        return parse_structured(self._raw_text, self.response_model)

    @property
    def json(self) -> JSONValue:
        """Returns parsed JSON. If 'json=True' was passed, this is highly reliable."""
        from .utils import parse_json
        return parse_json(self._raw_text)

    @property
    def pydantic(self) -> Any:
        """Returns parsed Pydantic model instance if response_model was provided."""
        if self.response_model is None:
            raise ValueError("No response_model was specified for this request.")
        return self.parsed

    def to_model(self, model_class: Any) -> Any:
        """Parse and validate the response text against a supported model."""
        from .structured import parse_structured
        return parse_structured(self._raw_text, model_class)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"<Response length={len(self._raw_text)}>"

    def save(self, path: str) -> None:
        """Smart save based on content type."""
        if self.media:
            self.media.save(path)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text)


class BaseProvider:
    """
    Abstract base class for all AI providers.
    Implements the core 'ask' logic and configuration management.
    """
    option_names = frozenset()

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        persona: str = None,
        strict_options: bool = False,
        **kwargs,
    ):
        self.strict_options = strict_options
        self._validate_option_names(kwargs, CONFIG_OPTION_NAMES | self.option_names, strict_options)
        # Zero-Config: Try env var if key not provided
        self.api_key = api_key or os.environ.get(self._get_api_key_env_var())
        self.model = model or self._get_default_model()
        self.persona = persona
        self.config = AdvancedConfig(**kwargs)
        self._middleware: list[Observability] = []
        self._retry_count_var = ContextVar(
            f"ask_ai_retry_count_{id(self)}", default=None
        )
        self._async_client_loop_ref = None

    def _check_async_client_loop(self) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        owner_ref = getattr(self, "_async_client_loop_ref", None)
        if owner_ref is None:
            self._async_client_loop_ref = weakref.ref(loop)
        elif owner_ref() is not loop:
            raise RuntimeError(
                "This provider's async client is bound to another event loop. "
                "Create a provider per loop or use one long-lived loop."
            )

    def close(self) -> None:
        """Close the provider's synchronous client, if it has one."""
        client = getattr(self, "client", None)
        close = getattr(client, "close", None)
        if callable(close):
            close()

    async def aclose(self) -> None:
        """Close the provider's asynchronous client, if it has one."""
        client = getattr(self, "_async_client", None)
        if client is not None:
            close = getattr(client, "aclose", None) or getattr(client, "close", None)
            if callable(close):
                result = close()
                if hasattr(result, "__await__"):
                    await result
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.aclose()

    @property
    def _retry_count(self) -> int:
        retry_count_var = getattr(self, "_retry_count_var", None)
        retry_count = retry_count_var.get() if retry_count_var is not None else None
        if retry_count is not None:
            return retry_count
        return getattr(self, "_last_retry_count", 0)

    @_retry_count.setter
    def _retry_count(self, value: int) -> None:
        retry_count_var = getattr(self, "_retry_count_var", None)
        if retry_count_var is None:
            retry_count_var = ContextVar(
                f"ask_ai_retry_count_{id(self)}", default=None
            )
            self._retry_count_var = retry_count_var
        retry_count_var.set(value)
        self._last_retry_count = value

    @staticmethod
    def _validate_option_names(options, allowed, strict=False):
        validate_option_names(options, allowed, strict)

    def use(self, middleware: Observability) -> "BaseProvider":
        """Attach optional observability middleware and return this provider."""
        self._middleware.append(middleware)
        return self

    def session(
        self,
        max_messages: Optional[int] = None,
        strict_options: Optional[bool] = None,
        **kwargs,
    ):
        strict = (
            getattr(self, "strict_options", False)
            if strict_options is None
            else strict_options
        )
        validate_option_names(kwargs, {"max_messages", "strict_options"}, strict)
        from .session import ConversationSession
        return ConversationSession(
            self,
            max_messages=max_messages,
            strict_options=strict,
        )

    def capabilities(self) -> Capabilities:
        """Return conservative capabilities for custom providers."""
        return Capabilities()

    def _attach_metadata(self, response: Response, started_at: float, retry_count: int) -> Response:
        usage = getattr(response, "usage", None)
        if isinstance(usage, dict):
            usage = Usage(**usage)
        metadata = ResponseMetadata(
            provider=self.__class__.__name__,
            model=self.model,
            latency_ms=(time.perf_counter() - started_at) * 1000,
            retry_count=retry_count,
            usage=usage,
            estimated_cost=None,
        )
        response.metadata = metadata
        for middleware in getattr(self, "_middleware", []):
            metadata = ResponseMetadata(
                **{**metadata.__dict__, "estimated_cost": middleware.cost(self.model, usage)}
            )
            response.metadata = metadata
            middleware.emit({"type": "completed", "metadata": metadata, "response": response})
        return response

    def _attach_failure_metadata(self, error: Exception, started_at: float) -> None:
        metadata = ResponseMetadata(
            provider=self.__class__.__name__,
            model=self.model,
            latency_ms=(time.perf_counter() - started_at) * 1000,
            retry_count=getattr(self, "_retry_count", 0),
            failure_reason=type(error).__name__,
        )
        for middleware in getattr(self, "_middleware", []):
            middleware.emit(
                {
                    "type": "failed",
                    "metadata": metadata,
                    "error": {
                        "provider": self.__class__.__name__,
                        "type": type(error).__name__,
                    },
                }
            )

    def _validation_retry_messages(
        self, messages: list[dict[str, str]], response: Response, error: StructuredValidationError
    ) -> list[dict[str, str]]:
        return [
            *messages,
            {"role": "assistant", "content": response.raw},
            {
                "role": "user",
                "content": (
                    "Your previous response failed schema validation: "
                    f"{error}. Return a corrected JSON response only."
                ),
            },
        ]

    def _execute_response(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
        output_type: Optional[str],
        retry: int,
        response_model: Any,
        validation_retries: int,
        started_at: float,
    ) -> Response:
        if validation_retries < 0:
            raise ValueError("validation_retries must be non-negative.")
        request_messages = messages
        retry_count = 0
        deadline = self._create_deadline(config)
        try:
            for attempt in range(validation_retries + 1):
                response = self._execute_with_retry(
                    self._send_request,
                    request_messages,
                    config,
                    output_type,
                    retry,
                    deadline=deadline,
                )
                response._kwargs.update(
                    {
                        option: config.extra[option]
                        for option in ("clean", "strip", "code")
                        if option in config.extra
                    }
                )
                retry_count += getattr(self, "_retry_count", 0)
                if response_model is None:
                    return self._attach_metadata(response, started_at, retry_count)
                response.response_model = response_model
                try:
                    response.parsed
                except StructuredValidationError as error:
                    if attempt == validation_retries:
                        raise
                    request_messages = self._validation_retry_messages(messages, response, error)
                else:
                    return self._attach_metadata(response, started_at, retry_count)
            raise RuntimeError("Structured validation retry loop exited unexpectedly.")
        except Exception as error:
            self._retry_count = retry_count + getattr(self, "_retry_count", 0)
            self._attach_failure_metadata(error, started_at)
            raise

    async def _execute_response_async(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
        output_type: Optional[str],
        retry: int,
        response_model: Any,
        validation_retries: int,
        started_at: float,
    ) -> Response:
        if validation_retries < 0:
            raise ValueError("validation_retries must be non-negative.")
        request_messages = messages
        retry_count = 0
        deadline = self._create_deadline(config)
        try:
            for attempt in range(validation_retries + 1):
                response = await self._execute_with_retry_async(
                    self._send_request_async,
                    request_messages,
                    config,
                    output_type,
                    retry,
                    deadline=deadline,
                )
                response._kwargs.update(
                    {
                        option: config.extra[option]
                        for option in ("clean", "strip", "code")
                        if option in config.extra
                    }
                )
                retry_count += getattr(self, "_retry_count", 0)
                if response_model is None:
                    return self._attach_metadata(response, started_at, retry_count)
                response.response_model = response_model
                try:
                    response.parsed
                except StructuredValidationError as error:
                    if attempt == validation_retries:
                        raise
                    request_messages = self._validation_retry_messages(messages, response, error)
                else:
                    return self._attach_metadata(response, started_at, retry_count)
            raise RuntimeError("Structured validation retry loop exited unexpectedly.")
        except Exception as error:
            self._retry_count = retry_count + getattr(self, "_retry_count", 0)
            self._attach_failure_metadata(error, started_at)
            raise

    def _get_api_key_env_var(self) -> str:
        """Subclasses should return the env var name, e.g. 'OPENAI_API_KEY'"""
        raise NotImplementedError

    def _get_default_model(self) -> str:
        """Subclasses should return a default model"""
        raise NotImplementedError

    def advanced(self, **kwargs) -> None:
        """
        Update global advanced settings for this instance.
        Merges new settings with existing ones.
        """
        strict = kwargs.pop("strict_options", self.strict_options)
        self._validate_option_names(kwargs, CONFIG_OPTION_NAMES | self.option_names, strict)
        new_conf = AdvancedConfig(**kwargs)
        for k, v in new_conf.__dict__.items():
            if k in ('extra', '_safe_mode_provided'):
                continue
            if k == 'safe_mode' and not new_conf._safe_mode_provided:
                continue
            if v is not None:
                setattr(self.config, k, v)
        if new_conf.extra:
            self.config.extra.update(new_conf.extra)

    # ─── Sync API ───────────────────────────────────────────

    def ask(self, query: str, **kwargs) -> Response:
        """
        The main entry point. Sync version.
        Detects intent, manages config, and returns a unified Response.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            last_error = None
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        if not self._is_retryable_error(e):
                            raise
                        last_error = e
                        errors.append(safe_provider_error_label(p.__name__, e))
                        continue
                else:
                    p_inst = p
                try:
                    return p_inst.ask(query, **kwargs)
                except Exception as e:
                    if not self._is_retryable_error(e):
                        raise
                    last_error = e
                    provider_name = p_inst.__class__.__name__
                    errors.append(safe_provider_error_label(provider_name, e))
                    logger.warning(
                        "Provider fallback failed for %s: %s",
                        provider_name,
                        type(e).__name__,
                    )
            raise ProviderError(f"All fallback providers failed: {errors}") from last_error

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        output_type = kwargs.get('output_type')
        retry = int(
            kwargs.get("retry", final_config.extra.get("retry", DEFAULT_RETRY_COUNT)) or 0
        )
        response_model = kwargs.get('response_model')
        validation_retries = int(kwargs.get("validation_retries", 0) or 0)

        started_at = time.perf_counter()
        return self._execute_response(
            messages, final_config, output_type, retry,
            response_model, validation_retries, started_at,
        )

    def ask_stream(self, query: str, **kwargs) -> Iterator[str]:
        """
        Streaming text generation. Yields text chunks.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            last_error = None
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        if not self._is_retryable_error(e):
                            raise
                        last_error = e
                        errors.append(safe_provider_error_label(p.__name__, e))
                        continue
                else:
                    p_inst = p
                try:
                    emitted = False
                    for chunk in p_inst.ask_stream(query, **kwargs):
                        emitted = True
                        yield chunk
                    return
                except Exception as e:
                    if emitted or not self._is_retryable_error(e):
                        raise
                    last_error = e
                    provider_name = p_inst.__class__.__name__
                    errors.append(safe_provider_error_label(provider_name, e))
                    logger.warning(
                        "Provider fallback failed for %s: %s",
                        provider_name,
                        type(e).__name__,
                    )
            raise ProviderError(f"All fallback providers failed: {errors}") from last_error

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        retry = int(
            kwargs.get("retry", final_config.extra.get("retry", DEFAULT_RETRY_COUNT))
            or 0
        )
        yield from self._iter_with_retry(
            lambda: self._send_request_stream(messages, final_config),
            retry,
            deadline=self._create_deadline(final_config),
            config=final_config,
        )

    def ask_stream_events(self, query: str, **kwargs) -> Iterator[Any]:
        """Yield typed events while preserving the legacy text stream API."""
        fallback_providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if fallback_providers:
            if not isinstance(fallback_providers, (list, tuple)):
                fallback_providers = [fallback_providers]
            last_error = None
            for provider in fallback_providers:
                emitted = False
                try:
                    provider_instance = provider() if isinstance(provider, type) else provider
                    for event in provider_instance.ask_stream_events(query, **kwargs):
                        if isinstance(event, Error):
                            if not emitted and event.emitted_chunks == 0:
                                if not self._is_retryable_error(event.error):
                                    yield event
                                    return
                                last_error = event
                                break
                            yield event
                            return
                        emitted = True
                        yield event
                    else:
                        return
                except Exception as error:
                    if emitted:
                        raise
                    if not self._is_retryable_error(error):
                        yield Error(error=error, emitted_chunks=0)
                        return
                    last_error = Error(error=error, emitted_chunks=0)
            if last_error is not None:
                yield last_error
            return

        emitted_chunks = 0
        text_parts = []
        usage = None
        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        retry = int(
            kwargs.get("retry", final_config.extra.get("retry", DEFAULT_RETRY_COUNT))
            or 0
        )
        try:
            for event in self._iter_with_retry(
                lambda: self._send_request_stream_events(messages, final_config),
                retry,
                deadline=self._create_deadline(final_config),
                config=final_config,
            ):
                if isinstance(event, TextDelta):
                    emitted_chunks += 1
                    text_parts.append(event.text)
                    yield event
                elif isinstance(event, UsageUpdate):
                    usage = event
                    yield event
                elif isinstance(event, ToolCall):
                    yield event
                else:
                    yield event
            yield Completed(response=Response(text="".join(text_parts)), usage=usage)
        except Exception as error:
            yield Error(error=error, emitted_chunks=emitted_chunks)

    # ─── Async API ──────────────────────────────────────────

    async def ask_async(self, query: str, **kwargs) -> Response:
        """
        Native async version of ask().
        Uses provider's async client directly — no thread pool wrapping.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            last_error = None
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        if not self._is_retryable_error(e):
                            raise
                        last_error = e
                        errors.append(safe_provider_error_label(p.__name__, e))
                        continue
                else:
                    p_inst = p
                try:
                    return await p_inst.ask_async(query, **kwargs)
                except Exception as e:
                    if not self._is_retryable_error(e):
                        raise
                    last_error = e
                    provider_name = p_inst.__class__.__name__
                    errors.append(safe_provider_error_label(provider_name, e))
                    logger.warning(
                        "Provider fallback failed for %s: %s",
                        provider_name,
                        type(e).__name__,
                    )
            raise ProviderError(f"All fallback providers failed: {errors}") from last_error

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        output_type = kwargs.get('output_type')
        retry = int(
            kwargs.get("retry", final_config.extra.get("retry", DEFAULT_RETRY_COUNT)) or 0
        )
        response_model = kwargs.get('response_model')
        validation_retries = int(kwargs.get("validation_retries", 0) or 0)

        started_at = time.perf_counter()
        return await self._execute_response_async(
            messages, final_config, output_type, retry,
            response_model, validation_retries, started_at,
        )

    async def ask_stream_async(self, query: str, **kwargs) -> AsyncIterator[str]:
        """
        Async streaming text generation. Yields text chunks.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            last_error = None
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        if not self._is_retryable_error(e):
                            raise
                        last_error = e
                        errors.append(safe_provider_error_label(p.__name__, e))
                        continue
                else:
                    p_inst = p
                try:
                    emitted = False
                    async for chunk in p_inst.ask_stream_async(query, **kwargs):
                        emitted = True
                        yield chunk
                    return
                except Exception as e:
                    if emitted or not self._is_retryable_error(e):
                        raise
                    last_error = e
                    provider_name = p_inst.__class__.__name__
                    errors.append(safe_provider_error_label(provider_name, e))
                    logger.warning(
                        "Provider fallback failed for %s: %s",
                        provider_name,
                        type(e).__name__,
                    )
            raise ProviderError(f"All fallback providers failed: {errors}") from last_error

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        retry = int(
            kwargs.get("retry", final_config.extra.get("retry", DEFAULT_RETRY_COUNT))
            or 0
        )
        async for chunk in self._aiter_with_retry(
            lambda: self._send_request_stream_async(messages, final_config),
            retry,
            deadline=self._create_deadline(final_config),
            config=final_config,
        ):
            yield chunk

    async def ask_stream_events_async(self, query: str, **kwargs) -> AsyncIterator[Any]:
        """Yield typed events while preserving the legacy async text stream API."""
        fallback_providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if fallback_providers:
            if not isinstance(fallback_providers, (list, tuple)):
                fallback_providers = [fallback_providers]
            last_error = None
            for provider in fallback_providers:
                emitted = False
                try:
                    provider_instance = provider() if isinstance(provider, type) else provider
                    async for event in provider_instance.ask_stream_events_async(query, **kwargs):
                        if isinstance(event, Error):
                            if not emitted and event.emitted_chunks == 0:
                                if not self._is_retryable_error(event.error):
                                    yield event
                                    return
                                last_error = event
                                break
                            yield event
                            return
                        emitted = True
                        yield event
                    else:
                        return
                except Exception as error:
                    if emitted:
                        raise
                    if not self._is_retryable_error(error):
                        yield Error(error=error, emitted_chunks=0)
                        return
                    last_error = Error(error=error, emitted_chunks=0)
            if last_error is not None:
                yield last_error
            return

        emitted_chunks = 0
        text_parts = []
        usage = None
        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        retry = int(
            kwargs.get("retry", final_config.extra.get("retry", DEFAULT_RETRY_COUNT))
            or 0
        )
        try:
            async for event in self._aiter_with_retry(
                lambda: self._send_request_stream_events_async(messages, final_config),
                retry,
                deadline=self._create_deadline(final_config),
                config=final_config,
            ):
                if isinstance(event, TextDelta):
                    emitted_chunks += 1
                    text_parts.append(event.text)
                    yield event
                elif isinstance(event, UsageUpdate):
                    usage = event
                    yield event
                elif isinstance(event, ToolCall):
                    yield event
                else:
                    yield event
            yield Completed(response=Response(text="".join(text_parts)), usage=usage)
        except Exception as error:
            yield Error(error=error, emitted_chunks=emitted_chunks)

    # ─── Config Helpers ─────────────────────────────────────

    def _build_final_config(self, kwargs: dict[str, Any]) -> AdvancedConfig:
        """Build final config by merging global config with per-request kwargs."""
        options = dict(kwargs)
        strict = options.pop("strict_options", getattr(self, "strict_options", False))
        validate_option_names(
            options,
            CONFIG_OPTION_NAMES
            | self.option_names
            | {"strict_options", "providers", "fallback"},
            strict,
        )
        if options.get("image") is not None:
            raise MediaTypeNotSupportedError(
                "Image input is not supported by the public ask() API yet."
            )
        output_type = options.get("output_type")
        if output_type not in (None, "text", "image", "audio"):
            raise ValueError(f"Unsupported output_type: {output_type!r}.")
        if output_type == "image" and not self.capabilities().image_generation:
            raise MediaTypeNotSupportedError(
                f"{self.__class__.__name__} does not support image generation."
            )
        if output_type == "audio" and not self.capabilities().audio_generation:
            raise MediaTypeNotSupportedError(
                f"{self.__class__.__name__} does not support audio generation."
            )
        request_config = AdvancedConfig(**options)
        final_config = self.config.merge(request_config)

        # Ensure timeout has a default
        timeout = options.get('timeout', final_config.extra.get('timeout', 30))
        final_config.extra['timeout'] = float(timeout) if timeout is not None else 30.0
        total_timeout = options.get(
            "total_timeout",
            final_config.extra.get("total_timeout"),
        )
        if total_timeout is not None:
            total_timeout = float(total_timeout)
            if not math.isfinite(total_timeout) or total_timeout <= 0:
                raise ValueError("total_timeout must be a finite positive number.")
            final_config.extra["total_timeout"] = total_timeout

        return final_config

    @staticmethod
    def _create_deadline(config: AdvancedConfig) -> Optional[float]:
        total_timeout = config.extra.get("total_timeout")
        if total_timeout is None:
            return None
        return time.monotonic() + float(total_timeout)

    @staticmethod
    def _apply_deadline(config: AdvancedConfig, deadline: Optional[float]) -> float:
        if deadline is None:
            return float("inf")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ProviderTimeoutError("Total request deadline exceeded.")
        configured_timeout = config.extra.get("timeout")
        if configured_timeout is None:
            config.extra["timeout"] = remaining
        else:
            config.extra["timeout"] = min(float(configured_timeout), remaining)
        return remaining

    def _prepare_messages(self, query: str, config: AdvancedConfig) -> list[dict[str, str]]:
        """Build the messages list from query, persona, and config."""
        messages = []

        system_msg = config.system_message or self.persona or ""

        # Smart capability: if json=True or response_model is specified
        response_model = config.extra.get('response_model')
        if response_model is not None:
            from .structured import json_schema_for_model

            schema = json_schema_for_model(response_model)
            if schema:
                import json
                schema_str = json.dumps(schema)
                json_instruction = (
                    f"You must respond with valid JSON matching the following JSON schema:\n"
                    f"{schema_str}\n"
                    f"Do not include any markdown markup, explanation, or HTML tags."
                )
            else:
                json_instruction = "You must respond with valid JSON only."

            system_msg = f"{system_msg}\n{json_instruction}".strip()
            config.extra['json'] = True

        elif config.extra.get('json'):
            json_instruction = "You must respond with valid JSON only, without any markdown formatting or tags."
            system_msg = f"{system_msg}\n{json_instruction}".strip()

        if system_msg:
            messages.append({"role": "system", "content": system_msg})

        messages.append({"role": "user", "content": query})
        return messages

    # ─── Retry Logic ────────────────────────────────────────

    def _iter_with_retry(
        self,
        iterator_factory,
        retry: int,
        deadline: Optional[float] = None,
        config: Optional[AdvancedConfig] = None,
    ):
        if retry < 0:
            raise ValueError("retry must be non-negative.")
        if deadline is None and config is not None:
            deadline = self._create_deadline(config)
        attempts = 0
        self._retry_count = 0
        while True:
            emitted = False
            iterator = None
            try:
                if config is not None:
                    self._apply_deadline(config, deadline)
                iterator = iter(iterator_factory())
                while True:
                    if config is not None:
                        self._apply_deadline(config, deadline)
                    try:
                        item = next(iterator)
                    except StopIteration:
                        break
                    if config is not None:
                        self._apply_deadline(config, deadline)
                    emitted = True
                    yield item
                self._retry_count = attempts
                return
            except Exception as error:
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total request deadline exceeded.") from error
                if emitted or attempts >= retry or not self._is_retryable_error(error):
                    raise
                attempts += 1
                self._retry_count = attempts
                delay = _retry_delay(error, attempts)
                logger.warning(
                    "Transient streaming error (%s). Retrying in %.1fs... (%d/%d)",
                    error.__class__.__name__,
                    delay,
                    attempts,
                    retry,
                )
                if config is not None:
                    remaining = self._apply_deadline(config, deadline)
                    if delay >= remaining:
                        time.sleep(remaining)
                        raise ProviderTimeoutError("Total request deadline exceeded.") from error
                time.sleep(delay)
            finally:
                close = getattr(iterator, "close", None)
                if close is not None:
                    close()

    async def _aiter_with_retry(
        self,
        iterator_factory,
        retry: int,
        deadline: Optional[float] = None,
        config: Optional[AdvancedConfig] = None,
    ):
        if retry < 0:
            raise ValueError("retry must be non-negative.")
        if deadline is None and config is not None:
            deadline = self._create_deadline(config)
        attempts = 0
        self._retry_count = 0
        while True:
            emitted = False
            iterator = None
            try:
                if config is not None:
                    self._apply_deadline(config, deadline)
                iterator = aiter(iterator_factory())
                while True:
                    if config is not None:
                        remaining = self._apply_deadline(config, deadline)
                    else:
                        remaining = float("inf")
                    try:
                        if deadline is None:
                            item = await anext(iterator)
                        else:
                            item = await asyncio.wait_for(anext(iterator), timeout=remaining)
                    except StopAsyncIteration:
                        break
                    except asyncio.TimeoutError as timeout_error:
                        raise ProviderTimeoutError(
                            "Total request deadline exceeded."
                        ) from timeout_error
                    emitted = True
                    yield item
                self._retry_count = attempts
                return
            except Exception as error:
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total request deadline exceeded.") from error
                if emitted or attempts >= retry or not self._is_retryable_error(error):
                    raise
                attempts += 1
                self._retry_count = attempts
                delay = _retry_delay(error, attempts)
                logger.warning(
                    "Transient async streaming error (%s). Retrying in %.1fs... (%d/%d)",
                    error.__class__.__name__,
                    delay,
                    attempts,
                    retry,
                )
                if config is not None:
                    remaining = self._apply_deadline(config, deadline)
                    if delay >= remaining:
                        await asyncio.sleep(remaining)
                        raise ProviderTimeoutError("Total request deadline exceeded.") from error
                await asyncio.sleep(delay)
            finally:
                close = getattr(iterator, "aclose", None)
                if close is not None:
                    await close()

    def _execute_with_retry(
        self,
        func,
        messages,
        config,
        output_type,
        retry,
        deadline: Optional[float] = None,
    ):
        """Execute a sync function with exponential backoff + jitter."""
        if retry < 0:
            raise ValueError("retry must be non-negative.")
        if deadline is None:
            deadline = self._create_deadline(config)
        attempts = 0
        last_error = None
        self._retry_count = 0

        while attempts <= retry:
            try:
                self._apply_deadline(config, deadline)
                response = func(messages, config, output_type)
                self._apply_deadline(config, deadline)
                self._retry_count = attempts
                return response
            except Exception as e:
                last_error = e
                if self._is_retryable_error(e) and attempts < retry:
                    attempts += 1
                    self._retry_count = attempts
                    delay = _retry_delay(e, attempts)
                    logger.warning(
                        "Transient error (%s). Retrying in %.1fs... (%d/%d)",
                        e.__class__.__name__, delay, attempts, retry
                    )
                    try:
                        remaining = self._apply_deadline(config, deadline)
                    except ProviderTimeoutError as timeout_error:
                        raise timeout_error from e
                    if delay >= remaining:
                        time.sleep(remaining)
                        raise ProviderTimeoutError("Total request deadline exceeded.") from e
                    time.sleep(delay)
                else:
                    raise

        from .exceptions import AskAINetworkError
        raise AskAINetworkError(f"Request failed after {retry} retries. Last error: {last_error}")

    async def _execute_with_retry_async(
        self,
        func,
        messages,
        config,
        output_type,
        retry,
        deadline: Optional[float] = None,
    ):
        """Execute an async function with exponential backoff + jitter."""
        if retry < 0:
            raise ValueError("retry must be non-negative.")
        if deadline is None:
            deadline = self._create_deadline(config)
        attempts = 0
        last_error = None
        self._retry_count = 0

        while attempts <= retry:
            try:
                remaining = self._apply_deadline(config, deadline)
                if deadline is None:
                    response = await func(messages, config, output_type)
                else:
                    response = await asyncio.wait_for(
                        func(messages, config, output_type),
                        timeout=remaining,
                    )
                self._apply_deadline(config, deadline)
                self._retry_count = attempts
                return response
            except asyncio.TimeoutError as timeout_error:
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total request deadline exceeded.") from timeout_error
                raise
            except Exception as e:
                last_error = e
                if self._is_retryable_error(e) and attempts < retry:
                    attempts += 1
                    self._retry_count = attempts
                    delay = _retry_delay(e, attempts)
                    logger.warning(
                        "Transient error (%s). Retrying in %.1fs... (%d/%d)",
                        e.__class__.__name__, delay, attempts, retry
                    )
                    try:
                        remaining = self._apply_deadline(config, deadline)
                    except ProviderTimeoutError as timeout_error:
                        raise timeout_error from e
                    if delay >= remaining:
                        await asyncio.sleep(remaining)
                        raise ProviderTimeoutError("Total request deadline exceeded.") from e
                    await asyncio.sleep(delay)
                else:
                    raise

        from .exceptions import AskAINetworkError
        raise AskAINetworkError(f"Request failed after {retry} retries. Last error: {last_error}")

    def _is_retryable_error(self, e: Exception) -> bool:
        """Dynamically detect rate limits and network timeouts across different provider SDKs."""
        from .exceptions import (
            AskAINetworkError,
            AskAIRateLimitError,
            ProviderRateLimitError,
            ProviderTimeoutError,
            ProviderUnavailableError,
        )
        if isinstance(e, (AskAINetworkError, AskAIRateLimitError, ProviderRateLimitError,
                          ProviderTimeoutError, ProviderUnavailableError)):
            return True
        return False

    # ─── Abstract Methods (Subclasses Must Implement) ──────

    def _send_request(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        """Sync request — subclasses must implement."""
        raise NotImplementedError

    async def _send_request_async(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        """Async request — subclasses should override for native async."""
        # Default fallback: run sync in thread pool
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._send_request, messages, config, output_type)

    def _send_request_stream(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        """Sync streaming — subclasses should override."""
        from .exceptions import StreamNotSupportedError
        raise StreamNotSupportedError(f"{self.__class__.__name__} does not support streaming.")

    def _send_request_stream_events(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Iterator[Any]:
        for index, chunk in enumerate(self._send_request_stream(messages, config)):
            yield TextDelta(text=chunk, index=index)

    async def _send_request_stream_async(self, messages: list[dict[str, str]], config: AdvancedConfig) -> AsyncIterator[str]:
        """Async streaming — subclasses should override for native async."""
        loop = asyncio.get_running_loop()
        items: asyncio.Queue[tuple[str, Any]] = asyncio.Queue(maxsize=1)
        stop = threading.Event()
        sentinel = object()

        def publish(item: tuple[str, Any]) -> bool:
            coroutine = items.put(item)
            try:
                future = asyncio.run_coroutine_threadsafe(coroutine, loop)
            except RuntimeError:
                coroutine.close()
                return False
            while not stop.is_set():
                try:
                    future.result(timeout=0.05)
                    return True
                except FutureTimeoutError:
                    continue
                except FutureCancelledError:
                    return False
            future.cancel()
            return False

        def produce() -> None:
            iterator = None
            failure = None
            try:
                iterator = iter(self._send_request_stream(messages, config))
                while not stop.is_set():
                    try:
                        chunk = next(iterator)
                    except StopIteration:
                        break
                    if not publish(("item", chunk)):
                        break
            except Exception as error:
                failure = error
            finally:
                close = getattr(iterator, "close", None)
                if close is not None:
                    try:
                        close()
                    except Exception as error:
                        if failure is None:
                            failure = error
                if not stop.is_set():
                    if failure is not None:
                        publish(("error", failure))
                    else:
                        publish(("done", sentinel))

        worker = threading.Thread(target=produce, name="ask-ai-sync-stream", daemon=True)
        worker.start()
        try:
            while True:
                kind, value = await items.get()
                if kind == "done":
                    return
                if kind == "error":
                    raise value
                yield value
        finally:
            stop.set()
            await asyncio.to_thread(worker.join, 0.1)

    async def _send_request_stream_events_async(
        self, messages: list[dict[str, str]], config: AdvancedConfig
    ) -> AsyncIterator[Any]:
        index = 0
        async for chunk in self._send_request_stream_async(messages, config):
            yield TextDelta(text=chunk, index=index)
            index += 1

    # ─── Tool Definitions for Smart Intent ─────────────────

    def _get_media_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": (
                        "Generate an image based on a prompt. Use this when the user asks to draw, create, or show an image."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The detailed description of the image to generate."
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_speech",
                    "description": (
                        "Generate audio speech from text. Use this when the user asks to say something, speak, or read aloud."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to speak."
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
