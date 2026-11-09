import asyncio
from types import SimpleNamespace

import pytest

from ask_ai import OpenAICompatibleProvider
from ask_ai.exceptions import ProviderConnectionError


class FakeCompletions:
    def __init__(self):
        self.calls = []
        self.fail = False

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise ConnectionError("connection refused")
        if kwargs.get("stream"):
            return iter(
                [
                    SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                delta=SimpleNamespace(content="sync chunk")
                            )
                        ],
                        usage=None,
                    )
                ]
            )
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="sync answer", tool_calls=None)
                )
            ],
            usage=None,
        )

    async def create_async(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise ConnectionError("connection refused")
        if kwargs.get("stream"):
            async def chunks():
                yield SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            delta=SimpleNamespace(content="async chunk")
                        )
                    ],
                    usage=None,
                )

            return chunks()
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="async answer", tool_calls=None)
                )
            ],
            usage=None,
        )


@pytest.fixture
def compatible_provider(monkeypatch):
    from ask_ai.providers import openai_compatible_provider

    completions = FakeCompletions()
    clients = []

    class SyncClient:
        def __init__(self, **kwargs):
            self.options = kwargs
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=completions.create)
            )
            clients.append(self)

        def close(self):
            pass

    class AsyncClient:
        def __init__(self, **kwargs):
            self.options = kwargs
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=completions.create_async)
            )
            clients.append(self)

        async def close(self):
            pass

    monkeypatch.setattr(
        openai_compatible_provider,
        "openai",
        SimpleNamespace(OpenAI=SyncClient, AsyncOpenAI=AsyncClient),
    )
    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1/",
        model="local-model",
        headers={"X-Test": "header"},
    )
    yield provider, completions, clients
    provider.close()


def test_generic_compatible_provider_validates_configuration(compatible_provider):
    provider, _completions, clients = compatible_provider
    assert provider.base_url == "http://localhost:8000/v1"
    assert provider.model == "local-model"
    assert clients[0].options["default_headers"] == {"X-Test": "header"}
    assert clients[0].options["api_key"] == "EMPTY"
    assert provider.capabilities().structured_output is False
    assert provider.capabilities().tool_calls is False
    assert provider.capabilities().image_generation is False
    assert provider.capabilities().vision is False


@pytest.mark.parametrize(
    ("base_url", "model", "message"),
    [
        ("not-a-url", "model", "absolute HTTP"),
        ("https://user:password@example.test/v1", "model", "credentials"),
        ("http://localhost/v1", None, "model is required"),
    ],
)
def test_generic_compatible_provider_rejects_bad_configuration(
    monkeypatch, base_url, model, message
):
    from ask_ai.providers import openai_compatible_provider

    monkeypatch.setattr(
        openai_compatible_provider,
        "openai",
        SimpleNamespace(OpenAI=lambda **_kwargs: None),
    )
    with pytest.raises(ValueError, match=message):
        OpenAICompatibleProvider(base_url=base_url, model=model)


def test_generic_compatible_provider_supports_all_four_transport_methods(
    compatible_provider,
):
    provider, completions, _clients = compatible_provider

    assert provider.ask("hello").text == "sync answer"
    assert list(provider.ask_stream("hello")) == ["sync chunk"]

    async def run_async_calls():
        assert (await provider.ask_async("hello")).text == "async answer"
        assert [
            chunk async for chunk in provider.ask_stream_async("hello")
        ] == ["async chunk"]
        await provider.aclose()

    asyncio.run(run_async_calls())
    assert [call["model"] for call in completions.calls] == ["local-model"] * 4
    assert "tools" not in completions.calls[0]


def test_generic_compatible_provider_maps_transport_errors(compatible_provider):
    provider, completions, _clients = compatible_provider
    completions.fail = True

    with pytest.raises(ProviderConnectionError):
        provider.ask("hello", retry=0)


def test_generic_compatible_provider_is_exported_from_package():
    from ask_ai.providers import OpenAICompatibleProvider as ProviderExport

    assert ProviderExport is OpenAICompatibleProvider
