import asyncio
from types import SimpleNamespace

import pytest

from ask_ai import AdvancedConfig, Observability, Usage
from ask_ai.providers.anthropic_provider import AnthropicProvider
from ask_ai.providers.azure_provider import AzureProvider
from ask_ai.providers.google_provider import GoogleProvider
from ask_ai.providers.groq_provider import GroqProvider
from ask_ai.providers.openai_provider import OpenAIProvider
from ask_ai.providers.openrouter_provider import OpenRouterProvider

EXPECTED_USAGE = Usage(input_tokens=12, output_tokens=7, total_tokens=19)
MESSAGES = [{"role": "user", "content": "hello"}]
CHAT_PROVIDER_CLASSES = (OpenAIProvider, AzureProvider, OpenRouterProvider, GroqProvider)


def _chat_response(usage):
    message = SimpleNamespace(content="answer", tool_calls=None)
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
        usage=usage,
    )


def _usage_source(provider_class):
    if provider_class is AnthropicProvider:
        return SimpleNamespace(input_tokens=12, output_tokens=7)
    if provider_class is GoogleProvider:
        return SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=7,
            total_token_count=19,
        )
    return SimpleNamespace(prompt_tokens=12, completion_tokens=7, total_tokens=19)


@pytest.mark.parametrize("provider_class", CHAT_PROVIDER_CLASSES)
def test_chat_provider_sync_response_includes_usage(provider_class):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: _chat_response(_usage_source(provider_class))
            )
        )
    )
    config = AdvancedConfig()

    response = provider._send_request(MESSAGES, config)

    assert response.usage == EXPECTED_USAGE


@pytest.mark.parametrize("provider_class", CHAT_PROVIDER_CLASSES)
def test_chat_provider_async_response_includes_usage(provider_class):
    provider = object.__new__(provider_class)
    provider.model = "test-model"

    async def create(**kwargs):
        return _chat_response(_usage_source(provider_class))

    provider._async_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    response = asyncio.run(provider._send_request_async(MESSAGES, AdvancedConfig()))

    assert response.usage == EXPECTED_USAGE


@pytest.mark.parametrize("provider_class", (AnthropicProvider, GoogleProvider))
def test_non_chat_provider_sync_response_includes_usage(provider_class, monkeypatch):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    if provider_class is AnthropicProvider:
        provider.client = SimpleNamespace(
            messages=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    content=[SimpleNamespace(text="answer")],
                    usage=_usage_source(provider_class),
                )
            )
        )
    else:
        response = SimpleNamespace(
            text="answer",
            usage_metadata=_usage_source(provider_class),
        )
        chat = SimpleNamespace(send_message=lambda *args, **kwargs: response)
        monkeypatch.setattr(
            provider,
            "_build_generation_config",
            lambda config: None,
            raising=False,
        )
        monkeypatch.setattr(
            provider,
            "_create_model",
            lambda system_instruction=None: SimpleNamespace(
                start_chat=lambda history: chat
            ),
            raising=False,
        )

    response = provider._send_request(MESSAGES, AdvancedConfig())

    assert response.usage == EXPECTED_USAGE


@pytest.mark.parametrize("provider_class", (AnthropicProvider, GoogleProvider))
def test_non_chat_provider_async_response_includes_usage(provider_class, monkeypatch):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    if provider_class is AnthropicProvider:

        async def create(**kwargs):
            return SimpleNamespace(
                content=[SimpleNamespace(text="answer")],
                usage=_usage_source(provider_class),
            )

        provider._async_client = SimpleNamespace(
            messages=SimpleNamespace(create=create)
        )
    else:
        response = SimpleNamespace(
            text="answer",
            usage_metadata=_usage_source(provider_class),
        )
        chat = SimpleNamespace(send_message=lambda *args, **kwargs: response)
        monkeypatch.setattr(
            provider,
            "_build_generation_config",
            lambda config: None,
            raising=False,
        )
        monkeypatch.setattr(
            provider,
            "_create_model",
            lambda system_instruction=None: SimpleNamespace(
                start_chat=lambda history: chat
            ),
            raising=False,
        )

    response = asyncio.run(provider._send_request_async(MESSAGES, AdvancedConfig()))

    assert response.usage == EXPECTED_USAGE


def test_missing_usage_stays_missing_instead_of_estimated():
    provider = object.__new__(OpenAIProvider)
    provider.model = "test-model"
    message = SimpleNamespace(content="answer", tool_calls=None)
    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[SimpleNamespace(message=message)],
                    usage=None,
                )
            )
        )
    )

    response = provider._send_request(MESSAGES, AdvancedConfig())

    assert response.usage is None


def test_usage_flows_to_public_observability_without_fabricated_cost():
    provider = object.__new__(OpenAIProvider)
    provider.model = "test-model"
    provider.config = AdvancedConfig()
    provider.persona = None
    provider._middleware = [
        Observability(pricing={"test-model": {"input": 1.0, "output": 1.0}})
    ]
    message = SimpleNamespace(content="answer", tool_calls=None)
    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(
                    choices=[SimpleNamespace(message=message)],
                    usage=None,
                )
            )
        )
    )

    response = provider.ask("hello")

    assert response.usage is None
    assert response.metadata.usage is None
    assert response.metadata.estimated_cost is None


@pytest.mark.parametrize("provider_class", CHAT_PROVIDER_CLASSES)
def test_chat_provider_stream_events_include_usage(provider_class):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    content_chunk = SimpleNamespace(
        choices=[SimpleNamespace(delta=SimpleNamespace(content="hello"))],
        usage=None,
    )
    usage_chunk = SimpleNamespace(choices=[], usage=_usage_source(provider_class))
    request = {}

    def create(**kwargs):
        request.update(kwargs)
        return iter([content_chunk, usage_chunk])

    provider.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=create
            )
        )
    )

    events = list(provider._send_request_stream_events(MESSAGES, AdvancedConfig()))

    assert events[0].text == "hello"
    assert events[1].input_tokens == 12
    assert events[1].output_tokens == 7
    assert request["stream_options"] == {"include_usage": True}


@pytest.mark.parametrize("provider_class", CHAT_PROVIDER_CLASSES)
def test_chat_provider_async_stream_events_include_usage(provider_class):
    provider = object.__new__(provider_class)
    provider.model = "test-model"

    class AsyncStream:
        def __init__(self):
            self.items = [
                SimpleNamespace(
                    choices=[SimpleNamespace(delta=SimpleNamespace(content="hello"))],
                    usage=None,
                ),
                SimpleNamespace(choices=[], usage=_usage_source(provider_class)),
            ]

        def __aiter__(self):
            self.iterator = iter(self.items)
            return self

        async def __anext__(self):
            try:
                return next(self.iterator)
            except StopIteration:
                raise StopAsyncIteration

    request = {}

    async def create(**kwargs):
        request.update(kwargs)
        return AsyncStream()

    provider._async_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    async def collect():
        return [
            event
            async for event in provider._send_request_stream_events_async(
                MESSAGES, AdvancedConfig()
            )
        ]

    events = asyncio.run(collect())

    assert events[0].text == "hello"
    assert events[1].input_tokens == 12
    assert events[1].output_tokens == 7
    assert request["stream_options"] == {"include_usage": True}


@pytest.mark.parametrize("provider_class", (AnthropicProvider, GoogleProvider))
def test_non_chat_provider_stream_events_include_usage(provider_class, monkeypatch):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    if provider_class is AnthropicProvider:

        class MessageStream:
            text_stream = ["hello"]

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def get_final_message(self):
                return SimpleNamespace(usage=_usage_source(provider_class))

        provider.client = SimpleNamespace(
            messages=SimpleNamespace(stream=lambda **kwargs: MessageStream())
        )
    else:
        chunks = [
            SimpleNamespace(text="hello", usage_metadata=None),
            SimpleNamespace(text="", usage_metadata=_usage_source(provider_class)),
        ]
        chat = SimpleNamespace(send_message=lambda *args, **kwargs: iter(chunks))
        monkeypatch.setattr(provider, "_build_generation_config", lambda config: None, raising=False)
        monkeypatch.setattr(
            provider,
            "_create_model",
            lambda system_instruction=None: SimpleNamespace(start_chat=lambda history: chat),
            raising=False,
        )

    events = list(provider._send_request_stream_events(MESSAGES, AdvancedConfig()))

    assert events[0].text == "hello"
    assert events[1].input_tokens == 12
    assert events[1].output_tokens == 7


@pytest.mark.parametrize("provider_class", (AnthropicProvider, GoogleProvider))
def test_non_chat_provider_async_stream_events_include_usage(provider_class, monkeypatch):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    if provider_class is AnthropicProvider:

        class MessageStream:
            async def __aenter__(self):
                self.text_stream = self._texts()
                return self

            async def __aexit__(self, *args):
                return None

            async def _texts(self):
                yield "hello"

            async def get_final_message(self):
                return SimpleNamespace(usage=_usage_source(provider_class))

        provider._async_client = SimpleNamespace(
            messages=SimpleNamespace(stream=lambda **kwargs: MessageStream())
        )
    else:
        chunks = [
            SimpleNamespace(text="hello", usage_metadata=None),
            SimpleNamespace(text="", usage_metadata=_usage_source(provider_class)),
        ]
        chat = SimpleNamespace(send_message=lambda *args, **kwargs: iter(chunks))
        monkeypatch.setattr(provider, "_build_generation_config", lambda config: None, raising=False)
        monkeypatch.setattr(
            provider,
            "_create_model",
            lambda system_instruction=None: SimpleNamespace(start_chat=lambda history: chat),
            raising=False,
        )

    async def collect():
        return [
            event
            async for event in provider._send_request_stream_events_async(
                MESSAGES, AdvancedConfig()
            )
        ]

    events = asyncio.run(collect())

    assert events[0].text == "hello"
    assert events[1].input_tokens == 12
    assert events[1].output_tokens == 7
