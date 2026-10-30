import logging
from collections.abc import AsyncIterator, Iterator

try:
    import anthropic
except ImportError:
    anthropic = None

from ..base import BaseProvider, Response
from ..capabilities import Capabilities
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, MediaTypeNotSupportedError, ProviderError, map_provider_exception

logger = logging.getLogger("ask_ai")


class AnthropicProvider(BaseProvider):
    def capabilities(self) -> Capabilities:
        return Capabilities(
            streaming=True,
            async_streaming=True,
            structured_output=True,
            vision=True,
        )

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("Anthropic API Key is missing. Set ANTHROPIC_API_KEY env var or pass api_key=")

        if anthropic is None:
            raise ProviderError("Anthropic client library not installed. Run: pip install anthropic")

        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            timeout=self.config.extra.get("timeout", 30.0),
        )
        self._async_client = None

    @property
    def async_client(self):
        """Lazy-load the async client only when needed."""
        if self._async_client is None:
            self._async_client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                timeout=self.config.extra.get("timeout", 30.0),
            )
        return self._async_client

    def _get_api_key_env_var(self):
        return "ANTHROPIC_API_KEY"

    def _get_default_model(self):
        return "claude-sonnet-4-20250514"

    # ─── Helpers ───────────────────────────────────────────

    def _convert_messages(self, messages: list[dict[str, str]]):
        """Convert OpenAI-style messages to Anthropic format."""
        anthropic_messages = []
        system_instruction = None

        for m in messages:
            role = m["role"]
            content = m["content"]
            if role == "system":
                system_instruction = content
            elif role in ("user", "assistant"):
                anthropic_messages.append({"role": role, "content": content})

        return anthropic_messages, system_instruction

    def _build_kwargs(self, messages: list[dict[str, str]], config: AdvancedConfig) -> dict:
        """Build kwargs for Anthropic messages.create."""
        anthropic_messages, system_instruction = self._convert_messages(messages)

        kwargs = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": config.max_tokens or 4096,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "timeout": config.extra.get("timeout"),
        }
        if system_instruction:
            kwargs["system"] = system_instruction

        return {k: v for k, v in kwargs.items() if v is not None}

    # ─── Sync ──────────────────────────────────────────────

    def _send_request(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError(f"Anthropic provider does not support {output_type} generation.")

        try:
            kwargs = self._build_kwargs(messages, config)
            response = self.client.messages.create(**kwargs)

            text_content = ""
            if response.content:
                text_content = response.content[0].text

            return Response(text=text_content)
        except Exception as e:
            raise map_provider_exception(e, "Anthropic", "API") from e

    def _send_request_stream(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        """Sync streaming with Anthropic."""
        try:
            kwargs = self._build_kwargs(messages, config)
            with self.client.messages.stream(**kwargs) as stream:
                yield from stream.text_stream
        except Exception as e:
            raise map_provider_exception(e, "Anthropic", "streaming") from e

    # ─── Async ─────────────────────────────────────────────

    async def _send_request_async(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError(f"Anthropic provider does not support {output_type} generation.")

        try:
            kwargs = self._build_kwargs(messages, config)
            response = await self.async_client.messages.create(**kwargs)

            text_content = ""
            if response.content:
                text_content = response.content[0].text

            return Response(text=text_content)
        except Exception as e:
            raise map_provider_exception(e, "Anthropic", "API") from e

    async def _send_request_stream_async(self, messages: list[dict[str, str]], config: AdvancedConfig) -> AsyncIterator[str]:
        """Async streaming with Anthropic."""
        try:
            kwargs = self._build_kwargs(messages, config)
            async with self.async_client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise map_provider_exception(e, "Anthropic", "streaming") from e
