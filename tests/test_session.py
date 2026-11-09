import asyncio
import threading
from dataclasses import dataclass

import pytest

from ask_ai import Observability
from ask_ai.base import BaseProvider, Response


class SessionProvider(BaseProvider):
    def _get_api_key_env_var(self):
        return "TEST_API_KEY"

    def _get_default_model(self):
        return "test"

    def _send_request(self, messages, config, output_type=None):
        return Response("|".join(message["content"] for message in messages))

    async def _send_request_async(self, messages, config, output_type=None):
        return self._send_request(messages, config, output_type)

    def _send_request_stream(self, messages, config):
        yield "|".join(message["content"] for message in messages)


def test_session_preserves_message_context_and_can_clear():
    session = SessionProvider(api_key="test").session()
    assert session.ask("one").text == "one"
    assert session.ask("two").text == "one|one|two"
    session.clear()
    assert session.ask("three").text == "three"


def test_session_limits_history():
    session = SessionProvider(api_key="test").session(max_messages=2)
    session.ask("one")
    session.ask("two")
    session.ask("three")
    assert len(session.messages) == 2
    assert [message["role"] for message in session.messages] == ["user", "assistant"]
    assert session.messages[0]["content"] == "three"


def test_session_uses_provider_observability():
    events = []
    provider = SessionProvider(api_key="test").use(Observability(on_event=events.append))

    response = provider.session().ask("hello")

    assert response.metadata.provider == "SessionProvider"
    assert events[0]["type"] == "completed"


def test_session_supports_structured_responses_and_rejects_streaming_validation():
    @dataclass
    class Result:
        value: str

    class StructuredProvider(SessionProvider):
        def _send_request(self, messages, config, output_type=None):
            return Response('{"value": "ok"}')

    session = StructuredProvider(api_key="test").session()

    assert session.ask("extract", response_model=Result).parsed == Result("ok")

    async def verify_async_apis():
        assert (
            await session.ask_async("extract", response_model=Result)
        ).parsed == Result("ok")

        with pytest.raises(NotImplementedError, match="not supported for streaming"):
            list(session.ask_stream("hello", response_model=Result))

        with pytest.raises(NotImplementedError, match="not supported for streaming"):
            [
                chunk
                async for chunk in session.ask_stream_async(
                    "hello", response_model=Result
                )
            ]

    asyncio.run(verify_async_apis())


def test_session_async_and_streaming():
    async def run():
        session = SessionProvider(api_key="test").session()
        await session.ask_async("one")
        chunks = [chunk async for chunk in session.ask_stream_async("two")]
        assert chunks == ["one|one|two"]

    asyncio.run(run())


def test_session_serializes_concurrent_sync_requests():
    first_complete = threading.Event()
    snapshots = []

    class BlockingProvider(SessionProvider):
        def _send_request(self, messages, config, output_type=None):
            snapshots.append([message["content"] for message in messages])
            if len(snapshots) == 1:
                first_complete.set()
            else:
                assert first_complete.is_set()
            return Response("ok")

    session = BlockingProvider(api_key="test").session()
    threads = [
        threading.Thread(target=session.ask, args=(prompt,))
        for prompt in ("first", "second")
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=2)
        assert not thread.is_alive()

    assert len(snapshots) == 2
    assert sorted(map(len, snapshots)) == [1, 3]
    assert snapshots[1][1] == "ok"


def test_session_serializes_concurrent_async_requests():
    snapshots = []
    first_complete = asyncio.Event()

    class BlockingProvider(SessionProvider):
        async def _send_request_async(self, messages, config, output_type=None):
            snapshots.append([message["content"] for message in messages])
            if len(snapshots) == 1:
                await asyncio.sleep(0)
                first_complete.set()
            else:
                assert first_complete.is_set()
            return Response("ok")

    session = BlockingProvider(api_key="test").session()

    async def run():
        await asyncio.gather(session.ask_async("first"), session.ask_async("second"))

    asyncio.run(run())
    assert len(snapshots) == 2
    assert sorted(map(len, snapshots)) == [1, 3]
    assert snapshots[1][1] == "ok"


def test_session_sync_stream_retries_before_first_chunk(monkeypatch):
    from ask_ai.exceptions import ProviderTimeoutError

    provider = SessionProvider(api_key="test")
    attempts = 0

    def stream(messages, config):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ProviderTimeoutError("temporary timeout")
        yield "recovered"

    monkeypatch.setattr(provider, "_send_request_stream", stream)
    monkeypatch.setattr("ask_ai.base.time.sleep", lambda delay: None)

    chunks = list(provider.session().ask_stream("hello", retry=1))

    assert chunks == ["recovered"]
    assert attempts == 2


def test_session_async_stream_retries_before_first_chunk(monkeypatch):
    from ask_ai.exceptions import ProviderTimeoutError

    provider = SessionProvider(api_key="test")
    attempts = 0

    async def stream(messages, config):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ProviderTimeoutError("temporary timeout")
        yield "recovered"

    async def no_sleep(delay):
        return None

    monkeypatch.setattr(provider, "_send_request_stream_async", stream)
    monkeypatch.setattr("ask_ai.base.asyncio.sleep", no_sleep)

    async def collect():
        return [chunk async for chunk in provider.session().ask_stream_async("hello", retry=1)]

    assert asyncio.run(collect()) == ["recovered"]
    assert attempts == 2
