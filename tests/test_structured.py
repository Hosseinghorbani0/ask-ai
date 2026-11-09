from dataclasses import dataclass
from typing import Literal, TypedDict

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


def test_response_to_model_validates_dataclass_field_types():
    with pytest.raises(StructuredValidationError, match="age"):
        Response('{"name": "Ada", "age": "wrong"}').to_model(User)
    assert Response('{"name": "Ada", "age": 37}').to_model(User) == User("Ada", 37)


def test_empty_json_schema_is_a_valid_response_model():
    assert Response("42", response_model={}).parsed == 42


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ("42", 42),
        ('"text"', "text"),
        ("true", True),
        ("null", None),
        ("[1, 2]", [1, 2]),
        ('{"key": "value"}', {"key": "value"}),
    ],
)
def test_response_json_returns_typed_json_values(payload, expected):
    assert Response(payload).json == expected


def test_dataclass_default_fields_are_applied_when_omitted():
    @dataclass
    class UserWithDefault:
        name: str
        active: bool = True

    assert parse_structured('{"name": "Ada"}', UserWithDefault) == UserWithDefault("Ada")


def test_invalid_literal_value_raises_structured_validation_error():
    @dataclass
    class Result:
        status: Literal["ok", "error"]

    with pytest.raises(StructuredValidationError, match="status"):
        parse_structured('{"status": "unknown"}', Result)


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


def test_release_version_is_0_6_1():
    import ask_ai

    assert ask_ai.__version__ == "0.6.1"
