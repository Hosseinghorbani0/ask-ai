import asyncio
import os
import subprocess
import sys
from contextlib import AbstractContextManager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, Optional, Union

import pytest

from ask_ai import (
    AdvancedConfig,
    Anthropic,
    Azure,
    Capabilities,
    Google,
    Groq,
    OpenAI,
    OpenAICompatibleProvider,
    OpenRouter,
)
from ask_ai.exceptions import (
    MediaTypeNotSupportedError,
    ProviderAuthError,
    ProviderConnectionError,
    ProviderError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    StructuredValidationError,
)

PROVIDER_CLASSES = [
    OpenAI,
    Anthropic,
    Google,
    Groq,
    Azure,
    OpenRouter,
    OpenAICompatibleProvider,
]
OPENAI_STYLE = {OpenAI, Groq, Azure, OpenRouter, OpenAICompatibleProvider}
OPTION_NAMES = {
    OpenAI: "max_tokens",
    Groq: "max_completion_tokens",
    Azure: "max_tokens",
    OpenRouter: "max_tokens",
    OpenAICompatibleProvider: "max_tokens",
    Anthropic: "max_tokens",
    Google: "max_output_tokens",
}
OPTION_PATHS = {
    OpenAI: ("max_tokens",),
    Groq: ("max_completion_tokens",),
    Azure: ("max_tokens",),
    OpenRouter: ("max_tokens",),
    OpenAICompatibleProvider: ("max_tokens",),
    Anthropic: ("max_tokens",),
    Google: ("config", "max_output_tokens"),
}
COMMON_OPTION_PATHS = {
    OpenAI: {
        "temperature": ("temperature",),
        "top_p": ("top_p",),
        "max_tokens": ("max_tokens",),
        "stop": ("stop",),
        "timeout": ("timeout",),
    },
    Groq: {
        "temperature": ("temperature",),
        "top_p": ("top_p",),
        "max_tokens": ("max_completion_tokens",),
        "stop": ("stop",),
        "timeout": ("timeout",),
    },
    Azure: {
        "temperature": ("temperature",),
        "top_p": ("top_p",),
        "max_tokens": ("max_tokens",),
        "stop": ("stop",),
        "timeout": ("timeout",),
    },
    OpenRouter: {
        "temperature": ("temperature",),
        "top_p": ("top_p",),
        "max_tokens": ("max_tokens",),
        "stop": ("stop",),
        "timeout": ("timeout",),
    },
    OpenAICompatibleProvider: {
        "temperature": ("temperature",),
        "top_p": ("top_p",),
        "max_tokens": ("max_tokens",),
        "stop": ("stop",),
        "timeout": ("timeout",),
    },
    Anthropic: {
        "temperature": ("temperature",),
        "top_p": ("top_p",),
        "max_tokens": ("max_tokens",),
        "stop": ("stop_sequences",),
        "timeout": ("timeout",),
    },
    Google: {
        "temperature": ("temperature",),
        "top_p": ("top_p",),
        "max_tokens": ("max_output_tokens",),
        "stop": ("stop_sequences",),
        "timeout": ("http_options", "timeout"),
    },
}


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


def _chat_response(text):
    return _ns(
        choices=[
            _ns(
                message=_ns(content=text, tool_calls=None),
                delta=_ns(content=text),
            )
        ],
        usage=_ns(prompt_tokens=2, completion_tokens=1, total_tokens=3),
    )


class _SyncStream(AbstractContextManager):
    def __init__(self, chunks):
        self.chunks = iter(chunks)
        self.closed = False
        self.text_stream = self

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.chunks)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.closed = True

    def close(self):
        self.closed = True


class _AsyncStream:
    def __init__(self, chunks, block_after_first=False):
        self.chunks = iter(chunks)
        self.closed = False
        self.text_stream = self
        self.block_after_first = block_after_first
        self.count = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.block_after_first and self.count == 1:
            await asyncio.Event().wait()
        try:
            chunk = next(self.chunks)
            self.count += 1
            return chunk
        except StopIteration:
            raise StopAsyncIteration

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.closed = True

    async def aclose(self):
        self.closed = True


class _FakeClient:
    def __init__(self, provider_class, async_mode=False):
        self.provider_class = provider_class
        self.async_mode = async_mode
        self.calls = []
        self.streams = []
        self.error = None
        self.error_after_chunk = False
        self.block_stream = False
        self.closed = False
        self.response_text = '{"value": "ok"}'
        self.messages = SimpleNamespace(create=self._create, stream=self._stream)
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )
        self.models = SimpleNamespace(
            generate_content=self._create,
            generate_content_stream=self._stream,
        )
        self.aio = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=self._async_create,
                generate_content_stream=self._astream,
            ),
            aclose=self._close_async_client,
        )
        self.chat.completions.create = (
            self._async_create if async_mode else self._create
        )
        self.messages.create = self._async_create if async_mode else self._create

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        if kwargs.get("stream"):
            if self.provider_class is Google:
                chunks = [_ns(text="first"), _ns(text="second")]
            elif self.provider_class is Anthropic:
                chunks = ["first", "second"]
            else:
                chunks = [_chat_response("first"), _chat_response("second")]
            if self.error_after_chunk:
                stream = _ErrorAfterChunkStream(chunks, async_mode=self.async_mode)
            elif self.async_mode:
                stream = _AsyncStream(chunks, block_after_first=self.block_stream)
            else:
                stream = _SyncStream(chunks)
            self.streams.append(stream)
            return stream
        if self.provider_class is Google:
            return _ns(text=self.response_text, usage_metadata=None)
        if self.provider_class is Anthropic:
            return _ns(
                content=[_ns(text=self.response_text)],
                usage=_ns(input_tokens=2, output_tokens=1),
            )
        return _chat_response(self.response_text)

    async def _async_create(self, **kwargs):
        return self._create(**kwargs)

    def _stream(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        if self.provider_class is Google:
            chunks = [_ns(text="first"), _ns(text="second")]
        elif self.provider_class is Anthropic:
            chunks = ["first", "second"]
        else:
            chunks = [_chat_response("first"), _chat_response("second")]
        if self.error_after_chunk:
            stream = _ErrorAfterChunkStream(chunks, async_mode=self.async_mode)
        elif self.async_mode:
            stream = _AsyncStream(chunks, block_after_first=self.block_stream)
        else:
            stream = _SyncStream(chunks)
        self.streams.append(stream)
        return stream

    def _astream(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        if self.provider_class is Google:
            chunks = [_ns(text="first"), _ns(text="second")]
        elif self.provider_class is Anthropic:
            chunks = ["first", "second"]
        else:
            chunks = [_chat_response("first"), _chat_response("second")]
        if self.error_after_chunk:
            stream = _ErrorAfterChunkStream(chunks, async_mode=True)
        else:
            stream = _AsyncStream(chunks, block_after_first=self.block_stream)
        self.streams.append(stream)
        return stream

    async def _close_async_client(self):
        self.closed = True

    def close(self):
        self.closed = True

    async def aclose(self):
        self.closed = True


class _ErrorAfterChunkStream(_SyncStream):
    def __init__(self, chunks, async_mode=False):
        self.chunks = iter(chunks)
        self.closed = False
        self.text_stream = self
        self.async_mode = async_mode
        self.count = 0

    def __next__(self):
        if self.count:
            raise ConnectionError("connection dropped after first chunk")
        self.count += 1
        return next(self.chunks)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return self.__next__()
        except StopIteration as error:
            raise StopAsyncIteration from error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.closed = True

    async def aclose(self):
        self.closed = True


class _ProviderCase:
    def __init__(self, provider_class):
        self.provider_class = provider_class
        self.provider = object.__new__(provider_class)
        provider = self.provider
        provider.model = "contract-model"
        provider.model_name = provider.model
        provider.persona = None
        provider.config = AdvancedConfig()
        provider.strict_options = False
        provider._middleware = []
        provider._retry_count_var = None
        provider._async_client_loop_ref = None
        if provider_class is OpenAICompatibleProvider:
            provider.base_url = "http://localhost:8000/v1"
            provider.api_key = "contract-key"
            provider.headers = {}

        self.sync_client = _FakeClient(provider_class)
        self.async_client = _FakeClient(provider_class, async_mode=True)
        if provider_class is Google:
            provider.client = self.sync_client
            provider.client.aio.aclose = self.async_client.aclose
        elif provider_class is Anthropic:
            provider.client = self.sync_client
            provider._async_client = self.async_client
        else:
            provider.client = self.sync_client
            provider._async_client = self.async_client

    @property
    def clients(self):
        return self.sync_client, self.async_client


@pytest.fixture(params=PROVIDER_CLASSES, ids=lambda cls: cls.__name__)
def provider_case(request):
    return _ProviderCase(request.param)


@dataclass
class _Result:
    value: str


class _Status(Enum):
    READY = "ready"


@dataclass
class _NestedResult:
    count: int


@dataclass
class _ComplexResult:
    nested: _NestedResult
    optional: Optional[str]
    choice: Union[int, str]
    status: _Status
    mode: Literal["safe", "fast"]


def test_provider_contract_sync_and_async_text(provider_case):
    provider = provider_case.provider
    assert provider.ask("hello", retry=0).text == '{"value": "ok"}'
    assert asyncio.run(provider.ask_async("hello", retry=0)).text == '{"value": "ok"}'


def test_provider_contract_imports_without_optional_sdk():
    code = """
import builtins
real_import = builtins.__import__
def import_without_openai(name, *args, **kwargs):
    optional_sdks = ("openai", "anthropic", "google", "groq")
    if any(name == sdk or name.startswith(sdk + ".") for sdk in optional_sdks):
        raise ImportError("optional SDK intentionally unavailable")
    return real_import(name, *args, **kwargs)
builtins.__import__ = import_without_openai
import ask_ai
from ask_ai import OpenAICompatibleProvider
from ask_ai.exceptions import ProviderError
try:
    OpenAICompatibleProvider(base_url="http://localhost:8000/v1", model="test")
except ProviderError as error:
    assert "pip install askai-python[openai]" in str(error)
else:
    raise AssertionError("missing SDK did not produce an install-extra error")
"""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=environment,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_provider_contract_sync_and_async_streaming(provider_case):
    provider = provider_case.provider
    assert list(provider.ask_stream("hello", retry=0)) == ["first", "second"]

    async def collect():
        return [chunk async for chunk in provider.ask_stream_async("hello", retry=0)]

    assert asyncio.run(collect()) == ["first", "second"]


def test_provider_contract_closes_streams_after_early_exit(provider_case):
    provider = provider_case.provider
    sync_stream = provider.ask_stream("hello", retry=0)
    assert next(sync_stream) == "first"
    sync_stream.close()
    assert provider_case.sync_client.streams[-1].closed

    async def close_async_stream():
        stream = provider.ask_stream_async("hello", retry=0)
        assert await anext(stream) == "first"
        await stream.aclose()

    asyncio.run(close_async_stream())
    async_stream_client = (
        provider_case.sync_client
        if provider_case.provider_class is Google
        else provider_case.async_client
    )
    assert async_stream_client.streams[-1].closed


def test_provider_contract_rejects_retries_after_emitting_a_chunk(provider_case):
    provider_case.sync_client.error_after_chunk = True
    with pytest.raises(ProviderConnectionError):
        list(provider_case.provider.ask_stream("hello", retry=2))
    assert len(provider_case.sync_client.calls) == 1

    async_stream_client = (
        provider_case.sync_client
        if provider_case.provider_class is Google
        else provider_case.async_client
    )
    async_calls_before = len(async_stream_client.calls)
    async_stream_client.error_after_chunk = True

    async def collect():
        with pytest.raises(ProviderConnectionError):
            [
                chunk
                async for chunk in provider_case.provider.ask_stream_async(
                    "hello", retry=2
                )
            ]

    asyncio.run(collect())
    assert len(async_stream_client.calls) == async_calls_before + 1


def test_provider_contract_async_stream_is_incremental_and_cancellable(provider_case):
    client = (
        provider_case.sync_client
        if provider_case.provider_class is Google
        else provider_case.async_client
    )
    client.block_stream = True

    async def consume_then_cancel():
        stream = provider_case.provider.ask_stream_async("hello", retry=0)
        assert await asyncio.wait_for(anext(stream), timeout=0.25) == "first"
        pending = asyncio.create_task(anext(stream))
        await asyncio.sleep(0)
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
        await stream.aclose()

    asyncio.run(consume_then_cancel())
    assert client.streams[-1].closed


def test_provider_contract_forwards_token_limit(provider_case):
    provider = provider_case.provider
    config = AdvancedConfig(max_tokens=41)
    provider._send_request([{"role": "user", "content": "hello"}], config)
    value = provider_case.sync_client.calls[-1]
    for key in OPTION_PATHS[provider_case.provider_class]:
        value = value[key]
    assert value == 41


def test_provider_contract_forwards_common_options(provider_case):
    provider = provider_case.provider
    config = AdvancedConfig(
        temperature=0.25,
        top_p=0.75,
        max_tokens=41,
        stop=["END"],
        timeout=7,
    )
    if provider_case.provider_class is Google:
        kwargs = provider._build_generation_config(config)
    elif provider_case.provider_class is Anthropic:
        kwargs = provider._build_kwargs(
            [{"role": "user", "content": "hello"}],
            config,
        )
    else:
        kwargs = provider._build_chat_kwargs(
            [{"role": "user", "content": "hello"}],
            config,
        )

    for option, path in COMMON_OPTION_PATHS[provider_case.provider_class].items():
        value = kwargs
        for key in path:
            value = value[key]
        expected = 7000 if option == "timeout" and provider_case.provider_class is Google else {
            "temperature": 0.25,
            "top_p": 0.75,
            "max_tokens": 41,
            "stop": ["END"],
            "timeout": 7,
        }[option]
        assert value == expected


def test_provider_contract_validates_structured_output(provider_case):
    result = provider_case.provider.ask(
        "extract",
        response_model=_Result,
        retry=0,
    )
    assert result.parsed == _Result("ok")


def test_provider_contract_validates_nested_union_enum_and_literal(provider_case):
    provider_case.sync_client.response_text = (
        '{"nested":{"count":3},"optional":null,"choice":"text",'
        '"status":"ready","mode":"safe"}'
    )
    result = provider_case.provider.ask(
        "extract",
        response_model=_ComplexResult,
        retry=0,
    )
    assert result.parsed == _ComplexResult(
        _NestedResult(3),
        None,
        "text",
        _Status.READY,
        "safe",
    )


def test_provider_contract_validates_pydantic_model(provider_case):
    pydantic = pytest.importorskip("pydantic")

    class Model(pydantic.BaseModel):
        value: str

    result = provider_case.provider.ask(
        "extract",
        response_model=Model,
        retry=0,
    )
    assert result.parsed.value == "ok"


def test_provider_contract_validates_pydantic_v1_model(provider_case):
    pytest.importorskip("pydantic")
    try:
        from pydantic.v1 import BaseModel
    except ImportError:
        pytest.skip("This Pydantic version does not expose the v1 compatibility API.")

    class Model(BaseModel):
        value: str

    result = provider_case.provider.ask(
        "extract",
        response_model=Model,
        retry=0,
    )
    assert result.parsed.value == "ok"


@pytest.mark.parametrize(
    "invalid_response",
    ['```json\n{"value":"ok"}\n```', '{"value":'],
)
def test_provider_contract_bounds_structured_validation_retries(
    provider_case, invalid_response
):
    provider_case.sync_client.response_text = invalid_response
    calls_before = len(provider_case.sync_client.calls)

    with pytest.raises(StructuredValidationError):
        provider_case.provider.ask(
            "extract",
            response_model=_Result,
            validation_retries=1,
            retry=0,
        )

    assert len(provider_case.sync_client.calls) - calls_before == 2


def test_provider_contract_maps_transport_errors(provider_case):
    provider_case.sync_client.error = ConnectionError("network detail")
    with pytest.raises(ProviderConnectionError):
        provider_case.provider._send_request(
            [{"role": "user", "content": "hello"}],
            AdvancedConfig(),
        )


@pytest.mark.parametrize(
    ("error", "expected_type"),
    [
        (RuntimeError("unauthorized"), ProviderAuthError),
        (RuntimeError("invalid request"), ProviderInvalidRequestError),
        (RuntimeError("rate limit"), ProviderRateLimitError),
        (TimeoutError("timeout"), ProviderTimeoutError),
        (ConnectionError("connection refused"), ProviderConnectionError),
    ],
)
def test_provider_contract_maps_sdk_error_categories(
    provider_case, error, expected_type
):
    provider_case.sync_client.error = error
    with pytest.raises(expected_type):
        provider_case.provider._send_request(
            [{"role": "user", "content": "hello"}],
            AdvancedConfig(),
        )


@pytest.mark.parametrize(
    ("error", "expected_type"),
    [
        (RuntimeError("unauthorized"), ProviderAuthError),
        (RuntimeError("invalid request"), ProviderInvalidRequestError),
        (RuntimeError("rate limit"), ProviderRateLimitError),
        (TimeoutError("timeout"), ProviderTimeoutError),
        (ConnectionError("connection refused"), ProviderConnectionError),
    ],
)
def test_provider_contract_maps_async_sdk_error_categories(
    provider_case, error, expected_type
):
    provider_case.sync_client.error = error
    provider_case.async_client.error = error

    async def send():
        with pytest.raises(expected_type):
            await provider_case.provider._send_request_async(
                [{"role": "user", "content": "hello"}],
                AdvancedConfig(),
            )

    asyncio.run(send())


def test_provider_contract_declares_conservative_capabilities(provider_case):
    provider = provider_case.provider
    capabilities = provider.capabilities()
    assert isinstance(capabilities, Capabilities)
    assert capabilities.vision is False
    with pytest.raises(MediaTypeNotSupportedError, match="Image input"):
        provider._build_final_config({"image": b"private"})


def test_provider_contract_closes_sync_and_async_clients(provider_case):
    provider = provider_case.provider
    provider.close()

    async def close_async():
        await provider.aclose()

    asyncio.run(close_async())
    assert provider_case.sync_client.closed
    assert provider_case.async_client.closed


def test_provider_contract_rejects_reuse_across_event_loops(provider_case):
    provider = provider_case.provider

    async def use_async_client():
        if provider_case.provider_class is Google:
            await provider._send_request_async(
                [{"role": "user", "content": "hello"}],
                AdvancedConfig(),
            )
        else:
            _ = provider.async_client

    asyncio.run(use_async_client())
    with pytest.raises(RuntimeError, match="another event loop"):
        asyncio.run(use_async_client())


def test_provider_contract_repr_does_not_expose_credentials_or_content(provider_case):
    provider = provider_case.provider
    if hasattr(provider, "api_key"):
        provider.api_key = "contract-secret-key"
    response = provider.ask("sensitive prompt", retry=0)
    assert "contract-secret-key" not in repr(provider)
    assert "sensitive prompt" not in repr(response)
    assert "contract-secret-key" not in repr(response)


def test_provider_contract_error_repr_does_not_expose_prompt_or_secret(provider_case):
    provider = provider_case.provider
    provider.api_key = "contract-secret-key"
    if hasattr(provider, "headers"):
        provider.headers = {"x-private-header": "contract-header-secret"}
    provider_case.sync_client.error = RuntimeError("private response body")

    with pytest.raises(ProviderError) as caught:
        provider._send_request(
            [{"role": "user", "content": "sensitive prompt"}],
            AdvancedConfig(),
        )
    rendered = repr(caught.value) + str(caught.value)
    assert str(caught.value.__cause__) == "private response body"
    assert "contract-secret-key" not in rendered
    assert "contract-header-secret" not in rendered
    assert "private response body" not in rendered
    assert "sensitive prompt" not in rendered
