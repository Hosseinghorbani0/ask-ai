from dataclasses import dataclass
from typing import TypedDict

import pytest

from ask_ai import AdvancedConfig, OpenAI
from ask_ai.base import Response
from ask_ai.exceptions import StructuredValidationError
from ask_ai.structured import parse_structured


@dataclass
class User:
    name: str
    age: int


class UserDict(TypedDict):
    name: str


def test_structured_response_supports_dataclass_and_typed_dict():
    assert parse_structured('{"name": "Ada", "age": 37}', User) == User("Ada", 37)
    assert parse_structured('{"name": "Ada"}', UserDict) == {"name": "Ada"}


def test_structured_response_exposes_raw_and_parsed():
    response = Response('{"name": "Ada", "age": 37}', response_model=User)
    assert response.raw == '{"name": "Ada", "age": 37}'
    assert response.parsed == User("Ada", 37)


def test_structured_response_rejects_invalid_data():
    with pytest.raises(StructuredValidationError):
        parse_structured('{"name": "Ada", "age": "wrong"}', User)


def test_structured_response_retries_validation_errors(monkeypatch):
    provider = object.__new__(OpenAI)
    provider.config = AdvancedConfig()
    provider.persona = None
    provider.model = "test"
    responses = iter([
        Response('{"name": "Ada", "age": "wrong"}'),
        Response('{"name": "Ada", "age": 37}'),
    ])
    provider._send_request = lambda messages, config, output_type: next(responses)
    provider._get_default_model = lambda: "test"

    result = provider.ask("extract", response_model=User, validation_retries=1)

    assert result.parsed == User("Ada", 37)

def test_structured_retry_includes_validation_feedback():
    provider = object.__new__(OpenAI)
    provider.config = AdvancedConfig()
    provider.persona = None
    provider.model = "test"
    captured_messages = []
    responses = iter([
        Response('{"name": "Ada", "age": "wrong"}'),
        Response('{"name": "Ada", "age": 37}'),
    ])

    def send_request(messages, config, output_type):
        captured_messages.append(messages)
        return next(responses)

    provider._send_request = send_request
    result = provider.ask("extract", response_model=User, validation_retries=1)

    assert result.parsed == User("Ada", 37)
    assert captured_messages[1][-2]["role"] == "assistant"
    assert captured_messages[1][-2]["content"] == '{"name": "Ada", "age": "wrong"}'
    assert "failed schema validation" in captured_messages[1][-1]["content"]


def test_pydantic_validation_exception_is_normalized():
    class Model:
        @classmethod
        def model_validate(cls, value):
            raise ValueError("invalid model")

    with pytest.raises(StructuredValidationError, match="invalid model"):
        parse_structured("{}", Model)


def test_release_version_is_0_6_0():
    import ask_ai

    assert ask_ai.__version__ == "0.6.0"
