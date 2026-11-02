import asyncio

from ask_ai.base import BaseProvider
from ask_ai.events import Completed, Error, TextDelta, ToolCall, UsageUpdate


class EventProvider(BaseProvider):
    def __init__(self, chunks, failure=None):
        super().__init__(api_key="test")
        self.chunks = chunks
        self.failure = failure

    def _get_api_key_env_var(self):
        return "TEST_API_KEY"

    def _get_default_model(self):
        return "test"

    def _send_request(self, messages, config, output_type=None):
        raise RuntimeError("not used")

    def _send_request_stream(self, messages, config):
        yield from self.chunks
        if self.failure:
            raise self.failure


class TypedEventProvider(EventProvider):
    def _send_request_stream_events(self, messages, config):
        yield ToolCall(name="lookup", arguments={"id": 1}, call_id="call-1")
        yield TextDelta(text="result", index=0)
        yield UsageUpdate(input_tokens=2, output_tokens=1, total_tokens=3)

    async def _send_request_stream_events_async(self, messages, config):
        yield ToolCall(name="lookup", arguments={"id": 1}, call_id="call-1")
        yield TextDelta(text="result", index=0)
        yield UsageUpdate(input_tokens=2, output_tokens=1, total_tokens=3)


def test_sync_stream_events_complete_and_preserve_legacy_stream():
    provider = EventProvider(["a", "b"])
    events = list(provider.ask_stream_events("hello"))

    assert [event.text for event in events if isinstance(event, TextDelta)] == ["a", "b"]
    assert isinstance(events[-1], Completed)
    assert events[-1].response.text == "ab"


def test_sync_stream_events_report_error_after_partial_output():
    events = list(EventProvider(["a"], RuntimeError("broken")).ask_stream_events("hello"))

    assert isinstance(events[-1], Error)
    assert events[-1].emitted_chunks == 1


def test_async_stream_events_complete():
    async def collect():
        provider = EventProvider(["a", "b"])
        return [event async for event in provider.ask_stream_events_async("hello")]

    events = asyncio.run(collect())
    assert isinstance(events[0], TextDelta)
    assert isinstance(events[-1], Completed)


def test_provider_typed_events_are_forwarded_in_sync_and_async():
    provider = TypedEventProvider([])
    sync_events = list(provider.ask_stream_events("hello"))
    assert any(isinstance(event, ToolCall) for event in sync_events)
    assert any(isinstance(event, UsageUpdate) for event in sync_events)
    assert sync_events[-1].usage == UsageUpdate(input_tokens=2, output_tokens=1, total_tokens=3)

    async def collect():
        return [event async for event in provider.ask_stream_events_async("hello")]

    async_events = asyncio.run(collect())
    assert any(isinstance(event, ToolCall) for event in async_events)
    assert any(isinstance(event, UsageUpdate) for event in async_events)
    assert async_events[-1].usage == UsageUpdate(input_tokens=2, output_tokens=1, total_tokens=3)


def test_sync_event_fallback_advances_after_pre_output_error():
    class FailedProvider:
        def __init__(self):
            self.calls = 0

        def ask_stream_events(self, query, **kwargs):
            self.calls += 1
            yield Error(RuntimeError("before first event"), emitted_chunks=0)

    class SuccessfulProvider:
        def __init__(self):
            self.calls = 0

        def ask_stream_events(self, query, **kwargs):
            self.calls += 1
            yield TextDelta(text="recovered", index=0)
            yield Completed(response=None)

    failed = FailedProvider()
    successful = SuccessfulProvider()
    events = list(EventProvider([]).ask_stream_events("hello", providers=[failed, successful]))

    assert failed.calls == 1
    assert successful.calls == 1
    assert [event.text for event in events if isinstance(event, TextDelta)] == ["recovered"]


def test_async_event_fallback_advances_after_pre_output_error():
    class FailedProvider:
        def __init__(self):
            self.calls = 0

        async def ask_stream_events_async(self, query, **kwargs):
            self.calls += 1
            yield Error(RuntimeError("before first event"), emitted_chunks=0)

    class SuccessfulProvider:
        def __init__(self):
            self.calls = 0

        async def ask_stream_events_async(self, query, **kwargs):
            self.calls += 1
            yield TextDelta(text="recovered", index=0)
            yield Completed(response=None)

    failed = FailedProvider()
    successful = SuccessfulProvider()

    async def collect():
        return [
            event
            async for event in EventProvider([]).ask_stream_events_async(
                "hello", providers=[failed, successful]
            )
        ]

    events = asyncio.run(collect())

    assert failed.calls == 1
    assert successful.calls == 1
    assert [event.text for event in events if isinstance(event, TextDelta)] == ["recovered"]
