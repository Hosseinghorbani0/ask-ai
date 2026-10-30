import asyncio

import pytest

from ask_ai import Capabilities, Router
from ask_ai.exceptions import ProviderInvalidRequestError, ProviderTimeoutError


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
