import asyncio

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


def test_session_async_and_streaming():
    async def run():
        session = SessionProvider(api_key="test").session()
        await session.ask_async("one")
        chunks = [chunk async for chunk in session.ask_stream_async("two")]
        assert chunks == ["one|one|two"]

    asyncio.run(run())
