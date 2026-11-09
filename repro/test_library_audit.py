import asyncio
import threading
import time

import pytest

from ask_ai import AdvancedConfig, Observability, Response, Router
from ask_ai.base import BaseProvider
from ask_ai.exceptions import (
    MediaTypeNotSupportedError,
    ProviderError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    StructuredValidationError,
)
from ask_ai.providers.anthropic_provider import AnthropicProvider
from ask_ai.providers.google_provider import GoogleProvider
from ask_ai.providers.openai_provider import OpenAIProvider
from ask_ai.structured import strict_json_schema


class MinimalProvider(BaseProvider):
    def __init__(self, send=None, **kwargs):
        self.send = send
        super().__init__(api_key="test", **kwargs)

    def _get_api_key_env_var(self):
        return "UNUSED"

    def _get_default_model(self):
        return "stub"

    def _send_request(self, messages, config, output_type=None):
        if self.send:
            return self.send(messages, config, output_type)
        return Response(messages[-1]["content"])

    def _send_request_stream(self, messages, config):
        yield from ("first", "second")


def test_session_max_messages_one_discards_the_entire_turn():
    session = MinimalProvider().session(max_messages=1)

    session.ask("remember me")

    assert session.messages == []


def test_session_concurrent_calls_serialize_turn_history():
    first_complete = threading.Event()
    observed = []

    def send(messages, config, output_type):
        observed.append([message["content"] for message in messages])
        if len(observed) == 1:
            first_complete.set()
        else:
            assert first_complete.is_set()
        return Response("ok")

    session = MinimalProvider(send=send).session()
    threads = [
        threading.Thread(target=session.ask, args=(prompt,))
        for prompt in ("first", "second")
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(observed) == 2
    assert len(observed[0]) == 1
    assert len(observed[1]) == 3
    assert observed[1][0] == observed[0][0]
    assert observed[1][1] == "ok"
    assert observed[1][2] in {"first", "second"}


def test_async_session_concurrent_calls_serialize_turn_history():
    observed = []
    first_complete = asyncio.Event()

    async def send(messages, config, output_type):
        observed.append([message["content"] for message in messages])
        if len(observed) == 1:
            await asyncio.sleep(0)
            first_complete.set()
        else:
            assert first_complete.is_set()
        return Response("ok")

    provider = MinimalProvider(send=lambda *args: None)
    async def async_send(messages, config, output_type=None):
        return await send(messages, config, output_type)

    provider._send_request_async = async_send
    session = provider.session()

    async def run():
        await asyncio.gather(session.ask_async("first"), session.ask_async("second"))

    asyncio.run(run())
    assert len(observed) == 2
    assert len(observed[0]) == 1
    assert len(observed[1]) == 3
    assert observed[1][0] == observed[0][0]
    assert observed[1][1] == "ok"


def test_plain_sync_stream_adapter_yields_before_source_finishes():
    class SlowProvider(MinimalProvider):
        def _send_request_stream(self, messages, config):
            yield "first"
            threading.Event().wait(0.5)
            yield "second"

    async def consume_one():
        stream = SlowProvider()._send_request_stream_async([], AdvancedConfig())
        try:
            return await asyncio.wait_for(anext(stream), timeout=0.25)
        finally:
            await stream.aclose()

    assert asyncio.run(consume_one()) == "first"


def test_provider_fallback_does_not_advance_after_invalid_request():
    calls = []

    class InvalidProvider(MinimalProvider):
        def _send_request(self, messages, config, output_type=None):
            calls.append("invalid")
            raise ProviderInvalidRequestError("bad user request")

    class SuccessProvider(MinimalProvider):
        def _send_request(self, messages, config, output_type=None):
            calls.append("success")
            return Response("ok")

    with pytest.raises(ProviderInvalidRequestError):
        InvalidProvider().ask(
            "question",
            providers=[InvalidProvider(), SuccessProvider()],
            retry=0,
        )

    assert calls == ["invalid"]


def test_router_max_attempts_bounds_provider_retry_multiplication(monkeypatch):
    calls = []

    class AlwaysRateLimited(MinimalProvider):
        def _send_request(self, messages, config, output_type=None):
            calls.append(self.model)
            raise ProviderRateLimitError("limited")

    monkeypatch.setattr("ask_ai.base.time.sleep", lambda _delay: None)
    providers = [AlwaysRateLimited(model="one"), AlwaysRateLimited(model="two")]

    with pytest.raises(ProviderError):
        Router(providers).ask("question", retry=2)

    assert calls == ["one", "two"]


def test_retry_after_hint_is_honored_and_clamped(monkeypatch):
    delays = []
    calls = []

    def send(messages, config, output_type):
        calls.append(1)
        if len(calls) == 1:
            error = ProviderRateLimitError("rate limited")
            error.retry_after = 17
            raise error
        if len(calls) == 2:
            error = ProviderRateLimitError("rate limited")
            error.retry_after = 100
            raise error
        return Response("ok")

    monkeypatch.setattr("ask_ai.base.random.uniform", lambda _a, _b: 0)
    monkeypatch.setattr("ask_ai.base.time.sleep", delays.append)

    assert MinimalProvider(send=send).ask("question", retry=2).text == "ok"
    assert delays == [17, 30]


def test_anthropic_forwards_common_stop_option():
    provider = object.__new__(AnthropicProvider)
    provider.model = "claude-test"

    kwargs = provider._build_kwargs(
        [{"role": "user", "content": "hello"}],
        AdvancedConfig(stop=["STOP"]),
    )

    assert kwargs["stop_sequences"] == ["STOP"]


def test_google_structured_capability_matches_native_schema_path():
    from dataclasses import dataclass

    @dataclass
    class Result:
        value: str

    provider = object.__new__(GoogleProvider)
    provider.model = "gemini-test"
    provider.model_name = provider.model
    config = AdvancedConfig(response_model=Result)
    _, request = provider._request_args(
        [{"role": "user", "content": "hello"}],
        config,
    )

    assert provider.capabilities().structured_output is True
    assert request["config"]["response_schema"] == strict_json_schema(Result)


def test_image_input_fails_explicitly_instead_of_being_dropped():
    with pytest.raises(MediaTypeNotSupportedError, match="Image input is not supported"):
        MinimalProvider().ask("describe this", image=b"image-bytes")


def test_to_model_validates_dataclass_field_types():
    from dataclasses import dataclass

    @dataclass
    class Result:
        count: int

    with pytest.raises(StructuredValidationError, match="count"):
        Response('{"count": "not-an-int"}').to_model(Result)
    assert Response('{"count": 3}').to_model(Result) == Result(3)


def test_empty_json_schema_accepts_arbitrary_json_values():
    response = Response("{}", response_model={})

    assert response.parsed == {}


def test_unknown_output_type_fails_instead_of_falling_through_to_text():
    provider = object.__new__(OpenAIProvider)
    called = []

    def generate(messages, config):
        called.append("text")
        return Response("text response")

    provider._generate_text_or_smart = generate

    with pytest.raises(ValueError, match="Unsupported output_type"):
        MinimalProvider().ask("hello", output_type="video")
    assert called == []


def test_response_json_returns_scalar_outside_its_declared_type():
    assert Response("42").json == 42


def test_provider_exposes_client_lifecycle_methods():
    assert callable(OpenAIProvider.close)
    assert callable(OpenAIProvider.__enter__)
    assert callable(OpenAIProvider.aclose)
    assert callable(OpenAIProvider.__aenter__)


def test_openai_async_client_rejects_reuse_between_event_loops(monkeypatch):
    from types import SimpleNamespace

    from ask_ai.providers import openai_provider

    created = []

    def make_client(**kwargs):
        client = object()
        created.append(client)
        return client

    monkeypatch.setattr(
        openai_provider,
        "openai",
        SimpleNamespace(OpenAI=make_client, AsyncOpenAI=make_client),
    )
    provider = OpenAIProvider(api_key="test")

    async def get_client():
        return provider.async_client

    first = asyncio.run(get_client())
    with pytest.raises(RuntimeError, match="bound to another event loop"):
        asyncio.run(get_client())

    assert first is not None
    assert len(created) == 2


def test_observability_callback_runs_synchronously_on_request_path():
    provider = MinimalProvider().use(
        Observability(on_event=lambda _event: time.sleep(0.03))
    )
    started = time.perf_counter()

    provider.ask("question")

    assert time.perf_counter() - started >= 0.03





def test_total_timeout_bounds_retry_and_backoff_wall_clock(monkeypatch):
    calls = []
    delays = []
    now = [100.0]

    class SlowTimeoutProvider(MinimalProvider):
        def _send_request(self, messages, config, output_type=None):
            calls.append(config.extra["timeout"])
            raise ProviderTimeoutError("timeout")

    def sleep(delay):
        delays.append(delay)
        now[0] += delay

    monkeypatch.setattr("ask_ai.base.random.uniform", lambda _a, _b: 0)
    monkeypatch.setattr("ask_ai.base.time.monotonic", lambda: now[0])
    monkeypatch.setattr("ask_ai.base.time.sleep", sleep)

    with pytest.raises(ProviderTimeoutError):
        SlowTimeoutProvider().ask("question", total_timeout=5, retry=3)

    assert calls == [5, 3]
    assert delays == [2, 3]
    assert now[0] == 105


def test_retry_repeats_a_request_after_a_simulated_billed_timeout(monkeypatch):
    calls = []

    class ChargedTimeoutProvider(MinimalProvider):
        def _send_request(self, messages, config, output_type=None):
            calls.append("charged")
            if len(calls) == 1:
                raise ProviderTimeoutError("response lost after billing")
            return Response("ok")

    monkeypatch.setattr("ask_ai.base.time.sleep", lambda _delay: None)

    assert ChargedTimeoutProvider().ask("question", retry=1).text == "ok"
    assert calls == ["charged", "charged"]


def test_failed_structured_response_double_counts_retries_in_failure_metadata(monkeypatch):
    events = []
    calls = []

    class RetryThenMalformedProvider(MinimalProvider):
        def _send_request(self, messages, config, output_type=None):
            calls.append(1)
            if len(calls) == 1:
                raise ProviderTimeoutError("timeout")
            return Response("not JSON")

    from dataclasses import dataclass

    @dataclass
    class Result:
        value: str

    monkeypatch.setattr("ask_ai.base.time.sleep", lambda _delay: None)
    provider = RetryThenMalformedProvider().use(
        Observability(on_event=events.append)
    )

    with pytest.raises(Exception, match="not valid JSON"):
        provider.ask("question", response_model=Result, retry=1)

    assert len(calls) == 2
    assert events[-1]["metadata"].retry_count == 2


def test_temp_media_files_remain_tracked_until_process_cleanup(tmp_path, monkeypatch):
    from ask_ai.media import TempFileManager

    created_before = set(TempFileManager._tracked_files)
    paths = [
        TempFileManager.create_temp_file(b"audio", ".mp3")
        for _ in range(3)
    ]

    assert all(path.exists() for path in paths)
    assert len(TempFileManager._tracked_files - created_before) == 3
    for path in paths:
        path.unlink(missing_ok=True)
        TempFileManager._tracked_files.discard(path)
