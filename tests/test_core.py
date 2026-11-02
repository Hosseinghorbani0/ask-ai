import asyncio
import importlib
import os
import pkgutil

import pytest

import ask_ai
from ask_ai import AdvancedConfig, Azure, OpenAI
from ask_ai.base import BaseProvider
from ask_ai.exceptions import (
    ProviderAuthError,
    ProviderConnectionError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    map_provider_exception,
)
from ask_ai.providers.openrouter_provider import OpenRouterProvider


def test_advanced_config_defaults():
    config = AdvancedConfig()
    assert config.temperature is None
    assert config.max_tokens is None
    assert config.system_message is None


def test_advanced_config_aliases():
    config = AdvancedConfig(prompt="System Prompt")
    assert config.system_message == "System Prompt"

    config2 = AdvancedConfig(system="System Prompt 2")
    assert config2.system_message == "System Prompt 2"


def test_provider_instantiation():
    # These should succeed with a fake key because clients are lazy-loaded or just stored
    # We set env var to None to ensure it uses the passed key
    os.environ.pop("OPENAI_API_KEY", None)

    ai = OpenAI(api_key="sk-fake-key-for-testing")
    assert ai.api_key == "sk-fake-key-for-testing"
    assert ai.model == "gpt-4o"  # Default model check


def test_azure_instantiation():
    az = Azure(
        api_key="fake",
        endpoint="https://example.com",
        api_version="2023-01-01",
        deployment_name="dep"
    )
    assert az.api_key == "fake"
    assert az.endpoint == "https://example.com"


def test_all_package_modules_and_providers_import():
    module_names = [
        module_info.name
        for module_info in pkgutil.walk_packages(ask_ai.__path__, f"{ask_ai.__name__}.")
    ]

    for module_name in module_names:
        importlib.import_module(module_name)

    for provider_name in ("OpenAI", "Anthropic", "Google", "Groq", "Azure", "OpenRouter"):
        assert getattr(ask_ai, provider_name)


def test_release_version_and_requirements_are_aligned():
    assert ask_ai.__version__ == "0.6.0rc1"
    pyproject = open("pyproject.toml", encoding="utf-8").read()
    assert f'version = "{ask_ai.__version__}"' in pyproject
    requirements = open("ask_ai/requirements.txt", encoding="utf-8").read()
    for package in ("openai", "anthropic>=1.0.0", "google-genai", "groq", "Pillow", "httpx"):
        assert package in requirements


def test_config_merge_preserves_safe_mode_when_request_omits_it():
    global_config = AdvancedConfig(safe_mode=True)
    request_config = AdvancedConfig()

    assert global_config.merge(request_config).safe_mode is True
    assert AdvancedConfig(retry=2).to_dict()["extra"]["retry"] == 2


def test_provider_exception_mapper_and_retry_policy():
    class ErrorWithStatus(Exception):
        def __init__(self, status_code):
            self.status_code = status_code

    assert isinstance(map_provider_exception(ErrorWithStatus(401), "Test"), ProviderAuthError)
    assert isinstance(map_provider_exception(ErrorWithStatus(429), "Test"), ProviderRateLimitError)
    assert isinstance(map_provider_exception(TimeoutError("timed out"), "Test"), ProviderTimeoutError)
    assert isinstance(map_provider_exception(ErrorWithStatus(422), "Test"), ProviderInvalidRequestError)
    assert isinstance(map_provider_exception(ErrorWithStatus(503), "Test"), ProviderUnavailableError)
    assert isinstance(
        map_provider_exception(type("APIConnectionError", (Exception,), {})("Connection error."), "Test"),
        ProviderConnectionError,
    )

    provider = object.__new__(BaseProvider)
    assert provider._is_retryable_error(ProviderRateLimitError("rate limited")) is True
    assert provider._is_retryable_error(ProviderInvalidRequestError("bad request")) is False


def test_default_retry_retries_transient_errors(monkeypatch):
    class TimeoutProvider(BaseProvider):
        def __init__(self):
            super().__init__(api_key="test")
            self.calls = 0

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            self.calls += 1
            if self.calls < 3:
                raise ProviderTimeoutError("timeout")
            return ask_ai.Response("ok")

    monkeypatch.setattr("ask_ai.base.time.sleep", lambda _delay: None)
    provider = TimeoutProvider()
    response = provider.ask("hello")

    assert response.text == "ok"
    assert provider.calls == 3


def test_default_retry_does_not_retry_auth_or_invalid_request_errors(monkeypatch):
    class FailingProvider(BaseProvider):
        def __init__(self, error):
            super().__init__(api_key="test")
            self.error = error
            self.calls = 0

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            self.calls += 1
            raise self.error

    monkeypatch.setattr("ask_ai.base.time.sleep", lambda _delay: None)
    for error in (
        ProviderAuthError("unauthorized"),
        ProviderInvalidRequestError("invalid request"),
    ):
        provider = FailingProvider(error)
        with pytest.raises(type(error)):
            provider.ask("hello")
        assert provider.calls == 1


def test_default_retry_applies_to_async_requests(monkeypatch):
    class AsyncTimeoutProvider(BaseProvider):
        def __init__(self):
            super().__init__(api_key="test")
            self.calls = 0

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        async def _send_request_async(self, messages, config, output_type=None):
            self.calls += 1
            if self.calls < 3:
                raise ProviderTimeoutError("timeout")
            return ask_ai.Response("ok")

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr("ask_ai.base.asyncio.sleep", no_sleep)
    provider = AsyncTimeoutProvider()
    response = asyncio.run(provider.ask_async("hello"))

    assert response.text == "ok"
    assert provider.calls == 3


def test_retry_zero_explicitly_disables_default_retries(monkeypatch):
    class TimeoutProvider(BaseProvider):
        def __init__(self):
            super().__init__(api_key="test")
            self.calls = 0

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            self.calls += 1
            raise ProviderTimeoutError("timeout")

    monkeypatch.setattr("ask_ai.base.time.sleep", lambda _delay: None)
    provider = TimeoutProvider()
    with pytest.raises(ProviderTimeoutError):
        provider.ask("hello", retry=0)

    assert provider.calls == 1


def test_openrouter_async_stream_retries_connection_before_first_chunk(monkeypatch):
    class APIConnectionError(Exception):
        pass

    class AsyncStream:
        def __init__(self):
            self.chunks = iter(
                [
                    type(
                        "Chunk",
                        (),
                        {
                            "choices": [
                                type(
                                    "Choice",
                                    (),
                                    {
                                        "delta": type(
                                            "Delta", (), {"content": "ready"}
                                        )()
                                    },
                                )()
                            ]
                        },
                    )()
                ]
            )

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.chunks)
            except StopIteration:
                raise StopAsyncIteration

    class Completions:
        def __init__(self):
            self.calls = 0
            self.fail_always = False

        async def create(self, **kwargs):
            self.calls += 1
            if self.fail_always or self.calls == 1:
                raise APIConnectionError("Connection error.")
            return AsyncStream()

    completions = Completions()
    provider = object.__new__(OpenRouterProvider)
    provider.model = "openai/gpt-4o"
    provider.persona = None
    provider.config = AdvancedConfig()
    provider.strict_options = False
    provider._async_client = type(
        "Client",
        (),
        {"chat": type("Chat", (), {"completions": completions})()},
    )()

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr("ask_ai.base.asyncio.sleep", no_sleep)

    async def collect():
        return [chunk async for chunk in provider.ask_stream_async("hello")]

    assert asyncio.run(collect()) == ["ready"]
    assert completions.calls == 2
    assert provider._retry_count == 1

    completions.fail_always = True

    async def collect_without_retry():
        with pytest.raises(
            ProviderConnectionError,
            match="OpenRouter streaming failed: Connection error",
        ):
            async for _chunk in provider.ask_stream_async("hello", retry=0):
                pass

    asyncio.run(collect_without_retry())
    assert completions.calls == 3


def test_sync_stream_retries_before_first_chunk(monkeypatch):
    class FlakyStreamProvider(BaseProvider):
        def __init__(self):
            super().__init__(api_key="test")
            self.calls = 0

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request_stream(self, messages, config):
            self.calls += 1
            if self.calls == 1:
                raise ProviderConnectionError("connection error")
            yield "ready"

    monkeypatch.setattr("ask_ai.base.time.sleep", lambda _delay: None)
    provider = FlakyStreamProvider()

    assert list(provider.ask_stream("hello")) == ["ready"]
    assert provider.calls == 2


def test_async_stream_does_not_retry_after_first_chunk(monkeypatch):
    class FailingStreamProvider(BaseProvider):
        def __init__(self):
            super().__init__(api_key="test")
            self.calls = 0

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        async def _send_request_stream_async(self, messages, config):
            self.calls += 1
            yield "first"
            raise ProviderConnectionError("connection dropped")

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr("ask_ai.base.asyncio.sleep", no_sleep)
    provider = FailingStreamProvider()

    async def collect():
        chunks = []
        with pytest.raises(ProviderConnectionError):
            async for chunk in provider.ask_stream_async("hello"):
                chunks.append(chunk)
        return chunks

    assert asyncio.run(collect()) == ["first"]
    assert provider.calls == 1


def test_async_stream_events_retry_before_first_event(monkeypatch):
    class EventsProvider(BaseProvider):
        def __init__(self):
            super().__init__(api_key="test")
            self.calls = 0

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        async def _send_request_stream_events_async(self, messages, config):
            self.calls += 1
            if self.calls == 1:
                raise ProviderConnectionError("connection error")
            yield ask_ai.TextDelta(text="ready", index=0)

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr("ask_ai.base.asyncio.sleep", no_sleep)
    provider = EventsProvider()

    async def collect():
        return [
            event
            async for event in provider.ask_stream_events_async("hello")
        ]

    events = asyncio.run(collect())
    assert provider.calls == 2
    assert isinstance(events[0], ask_ai.TextDelta)
    assert events[0].text == "ready"
    assert isinstance(events[-1], ask_ai.Completed)


def test_provider_request_timeout_is_forwarded():
    provider = object.__new__(OpenAI)
    provider.model = "test-model"
    config = AdvancedConfig(timeout=7)

    kwargs = provider._build_chat_kwargs(
        [{"role": "user", "content": "hello"}],
        config,
    )

    assert kwargs["timeout"] == 7.0


@pytest.mark.parametrize(
    ("option", "source", "expected"),
    [
        ("clean", "```json\n{\"ok\": true}\n```", "{\"ok\": true}"),
        ("strip", "<think>reasoning</think>answer", "answer"),
        ("code", "Example:\n```python\nprint('ok')\n```", "print('ok')"),
    ],
)
def test_text_formatting_options_work_through_public_ask(option, source, expected):
    class FormattingProvider(BaseProvider):
        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            from ask_ai import Response
            return Response(text=source)

    response = FormattingProvider(api_key="test").ask("format", **{option: True})

    assert response.text == expected
    assert response.raw == source


@pytest.mark.parametrize(
    ("option", "source", "expected"),
    [
        ("clean", "```json\n{\"ok\": true}\n```", "{\"ok\": true}"),
        ("strip", "<think>reasoning</think>answer", "answer"),
        ("code", "Example:\n```python\nprint('ok')\n```", "print('ok')"),
    ],
)
def test_text_formatting_options_work_through_public_ask_async(option, source, expected):
    class FormattingProvider(BaseProvider):
        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            from ask_ai import Response
            return Response(text=source)

    response = asyncio.run(
        FormattingProvider(api_key="test").ask_async("format", **{option: True})
    )

    assert response.text == expected
    assert response.raw == source


def test_provider_sdk_clients_disable_internal_retries(monkeypatch):
    from types import SimpleNamespace

    from ask_ai.providers import anthropic_provider, groq_provider, openai_provider

    clients = []

    def fake_client(*args, **kwargs):
        clients.append(kwargs)
        return object()

    monkeypatch.setattr(openai_provider, "openai", SimpleNamespace(
        OpenAI=fake_client,
        AsyncOpenAI=fake_client,
    ))
    monkeypatch.setattr(anthropic_provider, "anthropic", SimpleNamespace(
        Anthropic=fake_client,
        AsyncAnthropic=fake_client,
    ))
    monkeypatch.setattr(groq_provider, "Groq", fake_client)
    monkeypatch.setattr(groq_provider, "AsyncGroq", fake_client)

    OpenAI(api_key="test")
    openai_async = OpenAI(api_key="test")
    _ = openai_async.async_client
    anthropic = ask_ai.Anthropic(api_key="test")
    _ = anthropic.async_client
    groq = ask_ai.Groq(api_key="test")
    _ = groq.async_client

    assert len(clients) == 7
    assert all(client["max_retries"] == 0 for client in clients)


def test_azure_and_openrouter_sdk_clients_disable_internal_retries(monkeypatch):
    from ask_ai.providers import openrouter_provider

    clients = []

    def fake_client(*args, **kwargs):
        clients.append(kwargs)
        return object()

    monkeypatch.setattr(openrouter_provider.openai, "OpenAI", fake_client)
    monkeypatch.setattr(openrouter_provider.openai, "AsyncOpenAI", fake_client)
    monkeypatch.setattr(openrouter_provider.openai, "AzureOpenAI", fake_client)
    monkeypatch.setattr(openrouter_provider.openai, "AsyncAzureOpenAI", fake_client)

    azure = Azure(
        api_key="test",
        endpoint="https://example.test",
        deployment_name="deployment",
    )
    _ = azure.async_client
    router = ask_ai.OpenRouter(api_key="test")
    _ = router.async_client

    assert len(clients) == 4
    assert all(client["max_retries"] == 0 for client in clients)


def test_groq_uses_max_completion_tokens():
    from ask_ai import Groq

    provider = object.__new__(Groq)
    provider.model = "test-model"
    kwargs = provider._build_chat_kwargs(
        [{"role": "user", "content": "hello"}],
        AdvancedConfig(max_tokens=42),
    )

    assert kwargs["max_completion_tokens"] == 42
    assert "max_tokens" not in kwargs


def test_streaming_fallback_stops_after_first_provider_emits():
    class PartialProvider(BaseProvider):
        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            raise RuntimeError("not used")

        def _send_request_stream(self, messages, config):
            yield "partial"
            raise RuntimeError("stream interrupted")

    class FallbackProvider(PartialProvider):
        def _send_request_stream(self, messages, config):
            yield "fallback"

    provider = PartialProvider(api_key="test")
    stream = provider.ask_stream(
        "hello",
        providers=[PartialProvider(api_key="test"), FallbackProvider(api_key="test")],
    )

    assert next(stream) == "partial"
    try:
        next(stream)
    except RuntimeError as error:
        assert str(error) == "stream interrupted"
    else:
        raise AssertionError("stream failure should not switch providers after emission")


def test_openai_async_tool_call_uses_async_media_generation():
    class Function:
        name = "generate_image"
        arguments = '{"prompt": "a cat"}'

    class Message:
        content = None
        tool_calls = [type("ToolCall", (), {"function": Function()})()]

    response = type("Completion", (), {"choices": [type("Choice", (), {"message": Message()})()]})()
    provider = object.__new__(OpenAI)
    called = []

    async def fake_generate(messages, config):
        called.append(messages[-1]["content"])
        return type("Response", (), {"media": True})()

    provider._generate_image_async = fake_generate

    result = asyncio.run(provider._process_chat_response_async(response, [], AdvancedConfig()))

    assert called == ["a cat"]
    assert result.media is True


def test_cli_does_not_retry_streaming_failure_as_non_streaming(monkeypatch):
    from ask_ai import cli

    class FakeProvider:
        ask_calls = 0

        def __init__(self, **kwargs):
            pass

        def ask_stream(self, query, **kwargs):
            raise RuntimeError("stream failed")
            yield

        def ask(self, query, **kwargs):
            self.ask_calls += 1
            return type("Response", (), {"text": "fallback"})()

    monkeypatch.setattr(cli, "PROVIDER_MAP", {"openai": FakeProvider})
    monkeypatch.setattr("sys.argv", ["ask-ai", "--stream", "hello"])

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 1
    assert FakeProvider.ask_calls == 0


def test_async_streaming_fallback_accepts_async_generators():
    class TestProvider(BaseProvider):
        def __init__(self, chunks=None, **kwargs):
            super().__init__(api_key="test", **kwargs)
            self.chunks = chunks

        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            raise RuntimeError("not used")

        async def _send_request_stream_async(self, messages, config):
            if self.chunks is None:
                raise RuntimeError("first provider failed")
            for chunk in self.chunks:
                yield chunk

    async def collect():
        provider = TestProvider()
        return [
            chunk
            async for chunk in provider.ask_stream_async(
                "hello", providers=[TestProvider(), TestProvider(["ok"])]
            )
        ]

    assert asyncio.run(collect()) == ["ok"]


def test_openrouter_image_uses_bearer_auth_and_returns_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [{"url": "https://example.test/image.png"}]}

    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        return FakeResponse()

    monkeypatch.setattr("httpx.post", fake_post)
    monkeypatch.setattr(
        "ask_ai.providers.openai_provider._download_bytes",
        lambda url, timeout: b"\x89PNG\r\n\x1a\n",
    )

    provider = object.__new__(OpenRouterProvider)
    provider.api_key = "test-key"
    provider.model = "test-model"

    response = provider._generate_image(
        [{"role": "user", "content": "a cat"}],
        AdvancedConfig(timeout=30),
    )

    assert captured["url"] == "https://openrouter.ai/api/v1/images"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert response.media is not None
