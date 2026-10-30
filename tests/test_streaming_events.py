import asyncio

from ask_ai.base import BaseProvider
from ask_ai.events import Completed, Error, TextDelta


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
        for chunk in self.chunks:
            yield chunk
        if self.failure:
            raise self.failure


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
