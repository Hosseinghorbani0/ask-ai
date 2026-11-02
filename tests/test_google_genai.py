import asyncio
from pathlib import Path
from types import SimpleNamespace

from google.genai.errors import ClientError, ServerError

from ask_ai import AdvancedConfig
from ask_ai.exceptions import (
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderUnavailableError,
    map_provider_exception,
)
from ask_ai.providers import google_provider
from ask_ai.providers.google_provider import GoogleProvider

MESSAGES = [
    {"role": "system", "content": "Be concise."},
    {"role": "user", "content": "hello"},
    {"role": "assistant", "content": "hi"},
    {"role": "user", "content": "continue"},
]


def _response(text="answer"):
    return SimpleNamespace(
        text=text,
        usage_metadata=SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=7,
            total_token_count=19,
        ),
    )


def _provider():
    provider = object.__new__(GoogleProvider)
    provider.model = "test-model"
    provider.model_name = provider.model
    return provider


def test_google_provider_uses_google_genai_client_and_configured_timeout(monkeypatch):
    received = {}

    class FakeClient:
        def __init__(self, **kwargs):
            received.update(kwargs)

    monkeypatch.setattr(
        google_provider,
        "genai",
        SimpleNamespace(
            Client=FakeClient,
            types=SimpleNamespace(
                HttpOptions=lambda **kwargs: SimpleNamespace(**kwargs),
                HttpRetryOptions=lambda **kwargs: SimpleNamespace(**kwargs),
            ),
        ),
    )

    provider = GoogleProvider(api_key="test-key", timeout=8)

    assert received["api_key"] == "test-key"
    assert received["http_options"].timeout == 8000
    assert received["http_options"].retry_options.attempts == 1
    assert provider.client is not None


def test_google_genai_sync_request_preserves_conversation_and_usage():
    provider = _provider()
    request = {}

    def generate_content(**kwargs):
        request.update(kwargs)
        return _response()

    provider.client = SimpleNamespace(
        models=SimpleNamespace(generate_content=generate_content)
    )

    response = provider._send_request(MESSAGES, AdvancedConfig(timeout=4))

    assert request["model"] == "test-model"
    assert request["contents"] == [
        {"role": "user", "parts": ["hello"]},
        {"role": "model", "parts": ["hi"]},
        {"role": "user", "parts": ["continue"]},
    ]
    assert request["config"]["system_instruction"] == "Be concise."
    assert request["config"]["http_options"]["timeout"] == 4000
    assert request["config"]["http_options"]["retry_options"]["attempts"] == 1
    assert response.text == "answer"
    assert response.usage.input_tokens == 12
    assert response.usage.output_tokens == 7


def test_google_genai_async_request_uses_native_async_client():
    provider = _provider()
    request = {}

    async def generate_content(**kwargs):
        request.update(kwargs)
        return _response()

    provider.client = SimpleNamespace(
        aio=SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_content)
        )
    )

    response = asyncio.run(
        provider._send_request_async(MESSAGES, AdvancedConfig())
    )

    assert request["model"] == "test-model"
    assert response.text == "answer"
    assert response.usage.total_tokens == 19


def test_google_genai_sync_stream_uses_incremental_model_stream():
    provider = _provider()
    request = {}
    chunks = [SimpleNamespace(text="one"), SimpleNamespace(text="two")]

    def generate_content_stream(**kwargs):
        request.update(kwargs)
        yield from chunks

    provider.client = SimpleNamespace(
        models=SimpleNamespace(generate_content_stream=generate_content_stream)
    )

    assert list(provider._send_request_stream(MESSAGES, AdvancedConfig())) == [
        "one",
        "two",
    ]
    assert request["model"] == "test-model"


def test_google_genai_async_stream_is_native_and_incremental():
    provider = _provider()
    consumed = []

    async def generate_content_stream(**kwargs):
        for text in ("one", "two"):
            consumed.append(text)
            yield SimpleNamespace(text=text)

    provider.client = SimpleNamespace(
        aio=SimpleNamespace(
            models=SimpleNamespace(
                generate_content_stream=generate_content_stream
            )
        )
    )

    async def consume_one_then_finish():
        stream = provider._send_request_stream_async(MESSAGES, AdvancedConfig())
        first = await anext(stream)
        assert consumed == ["one"]
        second = await anext(stream)
        return first, second

    assert asyncio.run(consume_one_then_finish()) == ("one", "two")


def test_python_floor_and_ci_matrix_are_updated():
    project = Path("pyproject.toml").read_text(encoding="utf-8")
    ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert 'requires-python = ">=3.10"' in project
    assert '"3.9"' not in ci
    assert all(f'"3.{minor}"' in ci for minor in range(10, 14))
    assert "Python 3.10+" in readme


def test_google_genai_exception_codes_map_to_retry_and_auth_categories():
    cases = (
        (ClientError(401, {"message": "unauthorized"}), ProviderAuthError),
        (ClientError(403, {"message": "forbidden"}), ProviderAuthError),
        (ClientError(429, {"message": "rate limited"}), ProviderRateLimitError),
        (ServerError(500, {"message": "server error"}), ProviderUnavailableError),
        (ServerError(503, {"message": "unavailable"}), ProviderUnavailableError),
    )

    for error, expected in cases:
        assert isinstance(map_provider_exception(error, "Google"), expected)
