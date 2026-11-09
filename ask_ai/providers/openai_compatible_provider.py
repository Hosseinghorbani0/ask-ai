from collections.abc import AsyncIterator, Iterator
from types import ModuleType
from typing import Optional
from urllib.parse import urlsplit

from ..base import BaseProvider, Response
from ..capabilities import Capabilities
from ..config import CONFIG_OPTION_NAMES, AdvancedConfig
from ..exceptions import ProviderError
from .openai_provider import OpenAIProvider

openai: Optional[ModuleType]
try:
    import openai as openai_module
except ImportError:
    openai = None
else:
    openai = openai_module

class OpenAICompatibleProvider(OpenAIProvider):
    """Provider for servers implementing the OpenAI Chat Completions API."""

    provider_name = "OpenAI-compatible"

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        strict_options: bool = False,
        **kwargs,
    ):
        parsed_url = urlsplit(base_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
            raise ValueError("base_url must be an absolute HTTP or HTTPS URL.")
        if parsed_url.username is not None or parsed_url.password is not None:
            raise ValueError("base_url must not contain embedded credentials.")
        if not model:
            raise ValueError("model is required for an OpenAI-compatible provider.")
        if headers is not None and any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in headers.items()
        ):
            raise TypeError("headers must map strings to strings.")
        if openai is None:
            raise ProviderError("OpenAI client library not installed. Run: pip install askai-python[openai]")

        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers or {})
        self.strict_options = strict_options
        OpenAIProvider._validate_option_names(
            kwargs,
            CONFIG_OPTION_NAMES | self.option_names,
            strict_options,
        )
        BaseProvider.__init__(
            self,
            api_key=api_key or "EMPTY",
            model=model,
            strict_options=strict_options,
            **kwargs,
        )
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            default_headers=self.headers or None,
            timeout=self.config.extra.get("timeout", 30.0),
            max_retries=0,
        )
        self._async_client = None

    def capabilities(self) -> Capabilities:
        return Capabilities(streaming=True, async_streaming=True)

    def _get_api_key_env_var(self):
        return "OPENAI_API_KEY"

    def _get_default_model(self):
        return None

    @property
    def async_client(self):
        if self._async_client is None:
            self._async_client = openai.AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                default_headers=self.headers or None,
                timeout=self.config.extra.get("timeout", 30.0),
                max_retries=0,
            )
        self._check_async_client_loop()
        return self._async_client

    def _get_media_tools(self) -> list[dict]:
        return []

    def _build_chat_kwargs(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
        include_tools: bool = False,
    ) -> dict:
        return super()._build_chat_kwargs(messages, config, include_tools=False)

    def _send_request(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
        output_type: Optional[str] = None,
    ) -> Response:
        if output_type is None:
            return super()._send_request(messages, config)
        return super()._send_request(messages, config, output_type)

    async def _send_request_async(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
        output_type: Optional[str] = None,
    ) -> Response:
        if output_type is None:
            return await super()._send_request_async(messages, config)
        return await super()._send_request_async(messages, config, output_type)

    def _send_request_stream(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
    ) -> Iterator[str]:
        yield from super()._send_request_stream(messages, config)

    async def _send_request_stream_async(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
    ) -> AsyncIterator[str]:
        async for chunk in super()._send_request_stream_async(messages, config):
            yield chunk
