import logging
from collections.abc import AsyncIterator, Iterator

try:
    from groq import AsyncGroq, Groq
except ImportError:
    Groq = None
    AsyncGroq = None

from ..base import BaseProvider, Response
from ..capabilities import Capabilities
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, MediaTypeNotSupportedError, ProviderError, map_provider_exception

logger = logging.getLogger("ask_ai")


class GroqProvider(BaseProvider):
    def capabilities(self) -> Capabilities:
        return Capabilities(streaming=True, async_streaming=True, structured_output=True)

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("Groq API Key is missing. Set GROQ_API_KEY env var or pass api_key=")

        if Groq is None:
            raise ProviderError("Groq client library not installed. Run: pip install groq")

        self.client = Groq(api_key=self.api_key, timeout=self.config.extra.get("timeout", 30.0))
        self._async_client = None

    @property
    def async_client(self):
        """Lazy-load the async client only when needed."""
        if self._async_client is None:
            self._async_client = AsyncGroq(
                api_key=self.api_key,
                timeout=self.config.extra.get("timeout", 30.0),
            )
        return self._async_client

    def _get_api_key_env_var(self):
        return "GROQ_API_KEY"

    def _get_default_model(self):
        return "llama-3.3-70b-versatile"

    def _get_media_tools(self):
        # Groq doesn't support media generation, disable tools
        return []

    # ─── Helpers ───────────────────────────────────────────

    def _build_chat_kwargs(self, messages: list[dict[str, str]], config: AdvancedConfig) -> dict:
        """Build kwargs for chat.completions.create."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
            "timeout": config.extra.get("timeout"),
        }
        if config.stop:
            kwargs["stop"] = config.stop

        return {k: v for k, v in kwargs.items() if v is not None}

    # ─── Sync ──────────────────────────────────────────────

    def _send_request(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError(f"Groq provider does not support {output_type} generation.")

        try:
            kwargs = self._build_chat_kwargs(messages, config)
            response = self.client.chat.completions.create(**kwargs)
            return Response(text=response.choices[0].message.content or "")
        except Exception as e:
            raise map_provider_exception(e, "Groq", "API") from e

    def _send_request_stream(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        """Sync streaming with Groq."""
        try:
            kwargs = self._build_chat_kwargs(messages, config)
            kwargs["stream"] = True
            stream = self.client.chat.completions.create(**kwargs)

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise map_provider_exception(e, "Groq", "streaming") from e

    # ─── Async ─────────────────────────────────────────────

    async def _send_request_async(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError(f"Groq provider does not support {output_type} generation.")

        try:
            kwargs = self._build_chat_kwargs(messages, config)
            response = await self.async_client.chat.completions.create(**kwargs)
            return Response(text=response.choices[0].message.content or "")
        except Exception as e:
            raise map_provider_exception(e, "Groq", "API") from e

    async def _send_request_stream_async(self, messages: list[dict[str, str]], config: AdvancedConfig) -> AsyncIterator[str]:
        """Async streaming with Groq."""
        try:
            kwargs = self._build_chat_kwargs(messages, config)
            kwargs["stream"] = True
            stream = await self.async_client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise map_provider_exception(e, "Groq", "streaming") from e
