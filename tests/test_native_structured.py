import asyncio
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Optional, TypedDict

import pytest
from pydantic import BaseModel

from ask_ai import AdvancedConfig, Router
from ask_ai.base import BaseProvider, Response
from ask_ai.exceptions import ProviderError
from ask_ai.providers.anthropic_provider import AnthropicProvider
from ask_ai.providers.azure_provider import AzureProvider
from ask_ai.providers.google_provider import GoogleProvider
from ask_ai.providers.groq_provider import GroqProvider
from ask_ai.providers.openai_provider import OpenAIProvider
from ask_ai.providers.openrouter_provider import OpenRouterProvider
from ask_ai.structured import strict_json_schema


class Contact(BaseModel):
    name: str
    nickname: Optional[str] = None


@dataclass
class Address:
    city: str
    unit: Optional[int] = None


class ContactDict(TypedDict):
    name: str
    nickname: Optional[str]


MESSAGES = [{"role": "user", "content": "Extract a contact."}]


def _chat_response(text='{"name":"Ada","nickname":null}'):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=text, tool_calls=None)
            )
        ],
        usage=None,
    )


def _openai_provider(provider_class=OpenAIProvider):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    return provider


def _provider_with_create(provider_class, create, *, asynchronous=False):
    provider = object.__new__(provider_class)
    provider.model = "test-model"

    if provider_class is GoogleProvider:
        provider.model_name = provider.model
        models = SimpleNamespace(
            generate_content=create,
            generate_content_stream=create,
        )
        provider.client = SimpleNamespace(
            models=models,
            aio=SimpleNamespace(models=models),
        )
    elif provider_class is AnthropicProvider:
        messages = SimpleNamespace(create=create)
        client = SimpleNamespace(messages=messages)
        if asynchronous:
            provider._async_client = client
        else:
            provider.client = client
    else:
        completions = SimpleNamespace(create=create)
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions)
        )
        if asynchronous:
            provider._async_client = client
        else:
            provider.client = client
    return provider


def _provider_response(provider_class):
    if provider_class is GoogleProvider:
        return SimpleNamespace(
            text='{"name":"Ada","nickname":null}',
            usage_metadata=None,
        )
    if provider_class is AnthropicProvider:
        return SimpleNamespace(
            content=[SimpleNamespace(text='{"name":"Ada","nickname":null}')],
            usage=None,
        )
    return _chat_response()


def _native_format_for(provider_class, config):
    provider = object.__new__(provider_class)
    provider.model = "test-model"
    if provider_class is GoogleProvider:
        provider.model_name = provider.model
        _, request = provider._request_args(MESSAGES, config)
        return request["config"]
    if provider_class is AnthropicProvider:
        return provider._build_kwargs(MESSAGES, config)
    if provider_class is GroqProvider:
        return provider._build_chat_kwargs(MESSAGES, config)
    return provider._build_chat_kwargs(MESSAGES, config, include_tools=False)


@pytest.mark.parametrize(
    "provider_class",
    [
        OpenAIProvider,
        AzureProvider,
        OpenRouterProvider,
        AnthropicProvider,
        GroqProvider,
        GoogleProvider,
    ],
)
def test_native_schema_request_uses_provider_parameter_and_strict_schema(provider_class):
    config = AdvancedConfig(response_model=Contact)
    request = _native_format_for(provider_class, config)
    schema = strict_json_schema(Contact)

    assert schema["additionalProperties"] is False
    assert schema["required"] == ["name", "nickname"]
    assert schema["properties"]["nickname"]["anyOf"] == [
        {"type": "string"},
        {"type": "null"},
    ]

    if provider_class is GoogleProvider:
        assert request["response_mime_type"] == "application/json"
        assert request["response_schema"] == schema
    elif provider_class is AnthropicProvider:
        assert request["output_config"]["format"] == {
            "type": "json_schema",
            "schema": schema,
        }
    else:
        assert request["response_format"] == {
            "type": "json_schema",
            "json_schema": {
                "name": "Contact",
                "strict": True,
                "schema": schema,
            },
        }


def test_schema_derivation_supports_dataclass_typeddict_and_explicit_schema():
    address_schema = strict_json_schema(Address)
    assert address_schema["required"] == ["city", "unit"]
    assert address_schema["properties"]["unit"]["anyOf"] == [
        {"type": "integer"},
        {"type": "null"},
    ]
    typed_dict_schema = strict_json_schema(ContactDict)
    assert typed_dict_schema["required"] == ["name", "nickname"]
    assert typed_dict_schema["properties"]["nickname"]["anyOf"] == [
        {"type": "string"},
        {"type": "null"},
    ]
    schema = strict_json_schema(
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "alias": {"type": "string"},
            },
            "required": ["name"],
        }
    )
    assert schema["required"] == ["name", "alias"]
    assert schema["properties"]["alias"]["anyOf"] == [
        {"type": "string"},
        {"type": "null"},
    ]
    assert (
        strict_json_schema(
            {
                "type": "object",
                "properties": {},
                "additionalProperties": {"type": "string"},
            }
        )
        is None
    )


@pytest.mark.parametrize(
    "provider_class",
    [
        OpenAIProvider,
        AzureProvider,
        OpenRouterProvider,
        AnthropicProvider,
        GroqProvider,
        GoogleProvider,
    ],
)
@pytest.mark.parametrize("status_code", [400, 422])
def test_native_structured_request_and_unsupported_fallback(provider_class, status_code):
    calls = []

    class UnsupportedFormat(Exception):
        def __init__(self):
            super().__init__(
                "response_format json_schema is not supported with this model"
            )
            self.status_code = status_code

    def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise UnsupportedFormat()
        return _provider_response(provider_class)

    provider = _provider_with_create(provider_class, create)

    response = provider._send_request(
        MESSAGES, AdvancedConfig(response_model=Contact)
    )

    assert response.text == '{"name":"Ada","nickname":null}'
    if provider_class is GoogleProvider:
        assert calls[0]["config"]["response_mime_type"] == "application/json"
        assert "response_schema" not in calls[1]["config"]
    elif provider_class is AnthropicProvider:
        assert calls[0]["output_config"]["format"]["type"] == "json_schema"
        assert "output_config" not in calls[1]
    else:
        assert calls[0]["response_format"]["type"] == "json_schema"
        assert "response_format" not in calls[1]


@pytest.mark.parametrize(
    "provider_class",
    [
        OpenAIProvider,
        AzureProvider,
        OpenRouterProvider,
        AnthropicProvider,
        GroqProvider,
        GoogleProvider,
    ],
)
@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (401, "response_format json_schema is not supported"),
        (403, "response_format json_schema is not supported"),
        (429, "response_format json_schema is not supported"),
        (500, "response_format json_schema is not supported"),
        (503, "response_format json_schema is not supported"),
    ],
)
def test_auth_rate_limit_and_server_errors_never_trigger_prompt_fallback(
    provider_class, status_code, message
):
    calls = []

    class RequestError(Exception):
        def __init__(self):
            super().__init__(message)
            self.status_code = status_code

    def create(**kwargs):
        calls.append(kwargs)
        raise RequestError()

    provider = _provider_with_create(provider_class, create)

    with pytest.raises(ProviderError):
        provider._send_request(MESSAGES, AdvancedConfig(response_model=Contact))

    assert len(calls) == 1
    if provider_class is GoogleProvider:
        assert "response_schema" in calls[0]["config"]
    elif provider_class is AnthropicProvider:
        assert "output_config" in calls[0]
    else:
        assert "response_format" in calls[0]


def test_ambiguous_bad_request_does_not_trigger_prompt_fallback():
    provider = _openai_provider()
    calls = []

    class RequestError(Exception):
        status_code = 400

    def create(**kwargs):
        calls.append(kwargs)
        raise RequestError("invalid request")

    provider.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    with pytest.raises(ProviderError):
        provider._send_request(MESSAGES, AdvancedConfig(response_model=Contact))

    assert len(calls) == 1


def test_anthropic_native_schema_parameter():
    provider = object.__new__(AnthropicProvider)
    provider.model = "claude-test"
    kwargs = provider._build_kwargs(
        MESSAGES, AdvancedConfig(response_model=Contact)
    )

    assert kwargs["output_config"]["format"]["type"] == "json_schema"
    assert kwargs["output_config"]["format"]["schema"] == strict_json_schema(Contact)


def test_groq_native_schema_parameter():
    provider = object.__new__(GroqProvider)
    provider.model = "groq-test"
    kwargs = provider._build_chat_kwargs(
        MESSAGES, AdvancedConfig(response_model=Contact)
    )

    assert kwargs["response_format"]["json_schema"]["strict"] is True
    assert kwargs["response_format"]["json_schema"]["schema"] == strict_json_schema(Contact)


def test_google_native_schema_parameter():
    provider = object.__new__(GoogleProvider)
    provider.model = "gemini-test"
    provider.model_name = provider.model
    _, kwargs = provider._request_args(
        MESSAGES, AdvancedConfig(response_model=Contact)
    )

    assert kwargs["config"]["response_mime_type"] == "application/json"
    assert kwargs["config"]["response_schema"] == strict_json_schema(Contact)


def test_native_schema_fallback_works_in_async_openai_path():
    provider = _openai_provider()
    calls = []

    class UnsupportedFormat(Exception):
        status_code = 400

    async def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise UnsupportedFormat("json_schema is not supported")
        return _chat_response()

    provider._async_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    response = asyncio.run(
        provider._send_request_async(
            MESSAGES, AdvancedConfig(response_model=Contact)
        )
    )

    assert response.text == '{"name":"Ada","nickname":null}'
    assert len(calls) == 2
    assert "response_format" not in calls[1]


@pytest.mark.parametrize(
    "provider_class",
    [
        OpenAIProvider,
        AzureProvider,
        OpenRouterProvider,
        AnthropicProvider,
        GroqProvider,
        GoogleProvider,
    ],
)
def test_native_structured_output_is_sent_on_async_path(provider_class):
    calls = []

    async def create(**kwargs):
        calls.append(kwargs)
        return _provider_response(provider_class)

    provider = _provider_with_create(provider_class, create, asynchronous=True)
    response = asyncio.run(
        provider._send_request_async(
            MESSAGES, AdvancedConfig(response_model=Contact)
        )
    )

    assert response.text == '{"name":"Ada","nickname":null}'
    assert len(calls) == 1
    if provider_class is GoogleProvider:
        assert calls[0]["config"]["response_mime_type"] == "application/json"
    elif provider_class is AnthropicProvider:
        assert calls[0]["output_config"]["format"]["type"] == "json_schema"
    else:
        assert calls[0]["response_format"]["type"] == "json_schema"


def test_public_ask_keeps_raw_and_parsed_response_with_native_schema():
    provider = _openai_provider()
    provider.config = AdvancedConfig()
    provider.persona = None
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return _chat_response()

    provider.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    response = provider.ask("extract contact", response_model=Contact)

    assert response.raw == '{"name":"Ada","nickname":null}'
    assert response.parsed == Contact(name="Ada", nickname=None)
    assert captured["response_format"]["json_schema"]["strict"] is True
    assert "JSON schema" in captured["messages"][0]["content"]


def test_public_ask_async_keeps_raw_and_parsed_response_with_native_schema():
    provider = _openai_provider()
    provider.config = AdvancedConfig()
    provider.persona = None
    captured = {}

    async def create(**kwargs):
        captured.update(kwargs)
        return _chat_response()

    provider._async_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    response = asyncio.run(
        provider.ask_async("extract contact", response_model=Contact)
    )

    assert response.raw == '{"name":"Ada","nickname":null}'
    assert response.parsed == Contact(name="Ada", nickname=None)
    assert captured["response_format"]["json_schema"]["strict"] is True


def test_router_and_session_plain_requests_keep_existing_behavior():
    class PlainProvider(BaseProvider):
        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "test"

        def _send_request(self, messages, config, output_type=None):
            return Response(messages[-1]["content"])

    provider = PlainProvider(api_key="test")
    assert Router([provider]).ask("through router").text == "through router"
    assert provider.session().ask("through session").text == "through session"
