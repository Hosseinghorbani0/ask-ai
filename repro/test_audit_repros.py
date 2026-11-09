import asyncio
import threading
from dataclasses import dataclass
from typing import Literal

import pytest

from ask_ai import AdvancedConfig, Response, parse_structured
from ask_ai.base import BaseProvider
from ask_ai.exceptions import AskAIParsingError, StructuredValidationError
from ask_ai.utils import parse_json


class StubProvider(BaseProvider):
    def __init__(self):
        self.sent_messages = []
        super().__init__(api_key="test")
        self.persona = "You are a terse assistant."

    def _get_api_key_env_var(self):
        return "UNUSED_API_KEY"

    def _get_default_model(self):
        return "stub"

    def _send_request(self, messages, config, output_type=None):
        self.sent_messages.append(messages)
        return Response('{"name": "Ada"}')

    async def _send_request_async(self, messages, config, output_type=None):
        return self._send_request(messages, config, output_type)

    def _send_request_stream(self, messages, config):
        yield "first"
        yield "second"


def test_session_includes_provider_system_prompt():
    provider = StubProvider()

    provider.session().ask("hello")

    assert provider.sent_messages[0][0] == {
        "role": "system",
        "content": "You are a terse assistant.",
    }


def test_session_validates_structured_output():
    @dataclass
    class User:
        name: str

    response = StubProvider().session().ask("extract", response_model=User)

    assert response.parsed == User("Ada")


def test_dataclass_defaults_are_used_when_json_omits_optional_field():
    @dataclass
    class User:
        name: str
        active: bool = True

    assert parse_structured('{"name": "Ada"}', User) == User("Ada")


def test_literal_validation_raises_structured_validation_error():
    @dataclass
    class Result:
        status: Literal["ok", "error"]

    with pytest.raises(StructuredValidationError):
        parse_structured('{"status": "unknown"}', Result)


def test_retry_count_is_isolated_between_threads():
    provider = StubProvider()
    barrier = threading.Barrier(2)
    observed = {}

    def worker(name, count):
        provider._retry_count = count
        barrier.wait()
        observed[name] = provider._retry_count

    threads = [
        threading.Thread(target=worker, args=("one", 1)),
        threading.Thread(target=worker, args=("zero", 0)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert observed == {"one": 1, "zero": 0}


def test_retry_count_is_isolated_between_asyncio_tasks():
    provider = StubProvider()

    async def verify():
        first_set = asyncio.Event()
        second_set = asyncio.Event()

        async def first():
            provider._retry_count = 1
            first_set.set()
            await second_set.wait()
            return provider._retry_count

        async def second():
            await first_set.wait()
            provider._retry_count = 0
            second_set.set()
            return provider._retry_count

        return await asyncio.gather(first(), second())

    assert asyncio.run(verify()) == [1, 0]


def test_negative_retry_count_is_rejected_without_fabricated_network_error():
    provider = StubProvider()
    calls = []

    with pytest.raises(ValueError, match="retry"):
        provider._execute_with_retry(
            lambda *args: calls.append(args),
            [],
            AdvancedConfig(),
            None,
            -1,
        )

    assert calls == []


def test_response_repr_does_not_expose_provider_text():
    response = Response("customer-secret@example.test")

    assert "customer-secret" not in repr(response)


def test_json_parse_error_does_not_expose_response_content():
    secret = "customer-secret@example.test"

    with pytest.raises(AskAIParsingError) as error:
        parse_json(secret)

    assert secret not in str(error.value)


def test_default_async_stream_fallback_yields_before_sync_source_finishes():
    finished = threading.Event()

    class SlowStub(StubProvider):
        def _send_request_stream(self, messages, config):
            try:
                yield "first"
                threading.Event().wait(0.5)
                yield "second"
            finally:
                finished.set()

    async def consume():
        provider = SlowStub()
        stream = provider._send_request_stream_async([], AdvancedConfig())
        try:
            return await asyncio.wait_for(anext(stream), timeout=0.25)
        finally:
            await stream.aclose()

    assert asyncio.run(consume()) == "first"
    assert finished.wait(1)
