import asyncio

import pytest

from ask_ai import Capabilities, Router
from ask_ai.base import BaseProvider, Response
from ask_ai.exceptions import (
    ProviderError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)


class FakeProvider:
    def __init__(self, name, response, error=None):
        self.name = name
        self.response = response
        self.error = error

    def capabilities(self):
        return Capabilities(text=True, streaming=True)

    def ask(self, query, **kwargs):
        if self.error:
            raise self.error
        return self.response

    async def ask_async(self, query, **kwargs):
        return self.ask(query, **kwargs)

    def ask_stream(self, query, **kwargs):
        if self.error:
            raise self.error
        yield self.response

    async def ask_stream_async(self, query, **kwargs):
        if self.error:
            raise self.error
        yield self.response


def test_router_policy_and_retryable_fallback():
    slow = FakeProvider("slow", "slow")
    fast = FakeProvider("fast", "fast", ProviderTimeoutError("timeout"))
    router = Router(
        [slow, fast],
        policy="fastest",
        profiles={"FakeProvider": {"latency_ms": 10}},
    )
    assert router.ask("hello") == "slow"


def test_router_does_not_hide_invalid_request():
    provider = FakeProvider("bad", "unused", ProviderInvalidRequestError("bad"))
    with pytest.raises(ProviderInvalidRequestError):
        Router([provider]).ask("hello")


def test_router_async_and_streaming():
    async def run():
        router = Router([FakeProvider("one", "ok")])
        assert await router.ask_async("hello") == "ok"
        assert [chunk async for chunk in router.ask_stream_async("hello")] == ["ok"]

    asyncio.run(run())


def test_router_max_attempts_caps_provider_attempts_and_disables_nested_retries():
    calls = []

    class LimitedProvider(BaseProvider):
        def _get_api_key_env_var(self):
            return "TEST_API_KEY"

        def _get_default_model(self):
            return "limited"

        def _send_request(self, messages, config, output_type=None):
            calls.append(self.model)
            raise ProviderRateLimitError("limited")

    providers = [
        LimitedProvider(api_key="test", model="one"),
        LimitedProvider(api_key="test", model="two"),
        LimitedProvider(api_key="test", model="three"),
    ]

    with pytest.raises(ProviderError):
        Router(providers, max_attempts=2).ask("hello", retry=5)

    assert calls == ["one", "two"]


def test_router_total_deadline_is_shared_across_provider_fallbacks(monkeypatch):
    now = [10.0]
    seen_timeouts = []

    class FirstProvider:
        def ask(self, query, **kwargs):
            seen_timeouts.append(kwargs["total_timeout"])
            now[0] += 0.4
            raise ProviderTimeoutError("timeout")

    class SecondProvider:
        def ask(self, query, **kwargs):
            seen_timeouts.append(kwargs["total_timeout"])
            return Response("ok")

    monkeypatch.setattr("ask_ai.router.time.monotonic", lambda: now[0])

    response = Router([FirstProvider(), SecondProvider()], max_attempts=2).ask(
        "hello",
        total_timeout=1,
    )

    assert response.text == "ok"
    assert seen_timeouts == [1, pytest.approx(0.6)]
