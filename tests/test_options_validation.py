import asyncio
import warnings

import pytest

from ask_ai import AdvancedConfig, Azure
from ask_ai.base import BaseProvider, Response
from ask_ai.config import CONFIG_OPTION_NAMES
from ask_ai.providers.anthropic_provider import AnthropicProvider
from ask_ai.providers.openai_provider import OpenAIProvider
from ask_ai.providers.openrouter_provider import OpenRouterProvider


class OptionsProvider(BaseProvider):
    def _get_api_key_env_var(self):
        return "TEST_API_KEY"

    def _get_default_model(self):
        return "test"

    def _send_request(self, messages, config, output_type=None):
        self.last_config = config
        return Response("ok")

    async def _send_request_async(self, messages, config, output_type=None):
        return self._send_request(messages, config, output_type)

    def _send_request_stream(self, messages, config):
        self.last_config = config
        yield "ok"

    async def _send_request_stream_async(self, messages, config):
        self.last_config = config
        yield "ok"


@pytest.mark.parametrize("method_name", ["ask", "ask_async", "ask_stream", "ask_stream_async"])
def test_unknown_request_option_warns_with_suggestion(method_name):
    provider = OptionsProvider(api_key="test")
    with pytest.warns(UserWarning, match=r"Unknown option 'tempereture'.*temperature"):
        method = getattr(provider, method_name)
        if method_name == "ask_async":
            asyncio.run(method("hello", tempereture=0.2))
        elif method_name == "ask_stream_async":
            async def consume():
                return [chunk async for chunk in method("hello", tempereture=0.2)]

            asyncio.run(consume())
        elif method_name == "ask_stream":
            list(method("hello", tempereture=0.2))
        else:
            method("hello", tempereture=0.2)


def test_unknown_session_option_warns_with_suggestion():
    session = OptionsProvider(api_key="test").session()
    with pytest.warns(UserWarning, match=r"Unknown option 'tempereture'.*temperature"):
        session.ask("hello", tempereture=0.2)

    with pytest.warns(UserWarning, match=r"Unknown option 'max_messsages'.*max_messages"):
        OptionsProvider(api_key="test").session(max_messsages=4)


def test_strict_options_rejects_unknown_session_constructor_option():
    with pytest.raises(ValueError, match=r"Unknown option 'max_messsages'.*max_messages"):
        OptionsProvider(api_key="test").session(
            max_messsages=4,
            strict_options=True,
        )


def test_unknown_provider_constructor_option_warns():
    with pytest.warns(UserWarning, match=r"Unknown option 'tempereture'.*temperature"):
        OptionsProvider(api_key="test", tempereture=0.2)


def test_strict_options_rejects_unknown_request_and_constructor_options():
    with pytest.raises(ValueError, match=r"Unknown option 'tempereture'.*temperature"):
        OptionsProvider(api_key="test", strict_options=True, tempereture=0.2)

    provider = OptionsProvider(api_key="test")
    with pytest.raises(ValueError, match=r"Unknown option 'tempereture'.*temperature"):
        provider.ask("hello", tempereture=0.2, strict_options=True)


def test_known_forwarded_options_do_not_warn():
    provider = object.__new__(OpenAIProvider)
    provider.model = "test-model"
    with warnings.catch_warnings(record=True) as warnings_record:
        warnings.simplefilter("always")
        provider._validate_option_names(
            {"stop": ["END"], "timeout": 4},
            CONFIG_OPTION_NAMES | provider.option_names,
        )
        kwargs = provider._build_chat_kwargs(
            [{"role": "user", "content": "hello"}],
            AdvancedConfig(stop=["END"], timeout=4),
        )

    assert not warnings_record
    assert kwargs["stop"] == ["END"]
    assert kwargs["timeout"] == 4


def test_anthropic_forwards_stop_sequences():
    provider = object.__new__(AnthropicProvider)
    provider.model = "claude-test"

    kwargs = provider._build_kwargs(
        [{"role": "user", "content": "hello"}],
        AdvancedConfig(stop=["STOP"]),
    )

    assert kwargs["stop_sequences"] == ["STOP"]


def test_unknown_output_type_fails_before_request():
    provider = OptionsProvider(api_key="test")
    with pytest.raises(ValueError, match="Unsupported output_type"):
        provider.ask("hello", output_type="video")


def test_azure_constructor_options_are_accepted_without_warning():
    with warnings.catch_warnings(record=True) as warnings_record:
        warnings.simplefilter("always")
        Azure(
            api_key="test",
            endpoint="https://example.test",
            deployment_name="deployment",
            api_version="2024-06-01",
            timeout=5,
        )
    assert not warnings_record


def test_custom_provider_constructors_validate_options():
    with pytest.warns(UserWarning, match=r"Unknown option 'tempereture'.*temperature"):
        Azure(
            api_key="test",
            endpoint="https://example.test",
            deployment_name="deployment",
            tempereture=0.2,
        )

    with pytest.warns(UserWarning, match=r"Unknown option 'tempereture'.*temperature"):
        OpenRouterProvider(api_key="test", tempereture=0.2)

    with pytest.raises(ValueError, match=r"Unknown option 'tempereture'.*temperature"):
        OpenRouterProvider(api_key="test", strict_options=True, tempereture=0.2)


def test_safe_mode_warns_that_it_has_no_defined_behavior():
    with pytest.warns(DeprecationWarning, match="safe_mode is deprecated.*no defined behavior"):
        config = AdvancedConfig(safe_mode=True)
    assert config.safe_mode is True
