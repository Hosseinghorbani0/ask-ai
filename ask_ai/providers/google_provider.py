import logging
from collections.abc import AsyncIterator, Iterator

try:
    from google import genai
except ImportError:
    genai = None

from ..base import BaseProvider, Response
from ..capabilities import Capabilities
from ..config import AdvancedConfig
from ..events import TextDelta, UsageUpdate
from ..exceptions import APIKeyError, MediaTypeNotSupportedError, ProviderError, map_provider_exception
from ..observability import usage_from_fields
from ..structured import (
    call_with_schema_fallback,
    call_with_schema_fallback_async,
    strict_json_schema,
)

logger = logging.getLogger("ask_ai")


class GoogleProvider(BaseProvider):
    def capabilities(self) -> Capabilities:
        return Capabilities(
            streaming=True,
            async_streaming=True,
            structured_output=True,
            vision=False,
        )

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("Google API Key is missing. Set GOOGLE_API_KEY env var or pass api_key=")

        if genai is None:
            raise ProviderError("Google Gen AI library not installed. Run: pip install google-genai")

        self.client = self._create_client(self._timeout_ms(self.config))
        self.model_name = self.model

    def _get_api_key_env_var(self):
        return "GOOGLE_API_KEY"

    def _get_default_model(self):
        return "gemini-2.0-flash"

    @staticmethod
    def _timeout_ms(config: AdvancedConfig) -> int:
        timeout = config.extra.get("timeout")
        if timeout is None:
            timeout = 30
        return max(0, round(float(timeout) * 1000))

    def _create_client(self, timeout_ms: int):
        return genai.Client(
            api_key=self.api_key,
            http_options=genai.types.HttpOptions(
                timeout=timeout_ms,
                retry_options=genai.types.HttpRetryOptions(attempts=1),
            ),
        )

    def close(self) -> None:
        """Close the synchronous Google SDK client."""
        if hasattr(self, "client"):
            self.client.close()

    async def aclose(self) -> None:
        """Close the asynchronous Google SDK client."""
        if hasattr(self, "client"):
            await self.client.aio.aclose()
            self.close()

    # ─── Message and request helpers ───────────────────────

    def _convert_messages(self, messages: list[dict[str, str]]):
        """Convert OpenAI-style messages to Gemini content dictionaries."""
        gemini_messages = []
        system_instruction = None

        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                system_instruction = content
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})

        return gemini_messages, system_instruction

    def _build_generation_config(self, config: AdvancedConfig, system_instruction=None):
        values = {
            "candidate_count": 1,
            "max_output_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "stop_sequences": config.stop,
            "system_instruction": system_instruction,
            "http_options": {
                "timeout": self._timeout_ms(config),
                "retry_options": {"attempts": 1},
            },
        }
        response_model = config.extra.get("response_model")
        schema = strict_json_schema(response_model) if response_model is not None else None
        if schema is not None:
            values["response_mime_type"] = "application/json"
            values["response_schema"] = schema
        return {
            key: value
            for key, value in values.items()
            if value is not None or key == "http_options"
        }

    def _request_args(self, messages, config):
        contents, system_instruction = self._convert_messages(messages)
        return contents, {
            "model": getattr(self, "model_name", self.model),
            "contents": contents,
            "config": self._build_generation_config(config, system_instruction),
        }

    @staticmethod
    def _usage(response):
        return usage_from_fields(
            getattr(response, "usage_metadata", None),
            "prompt_token_count",
            "candidates_token_count",
            "total_token_count",
        )

    # ─── Sync ──────────────────────────────────────────────

    def _send_request(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError("Google provider currently supports text generation primarily.")

        try:
            contents, request = self._request_args(messages, config)
            if not contents:
                return Response(text="")

            response_model = config.extra.get("response_model")
            schema = strict_json_schema(response_model) if response_model is not None else None
            if schema is not None:
                fallback_request = dict(request)
                fallback_config = dict(request["config"])
                fallback_config.pop("response_mime_type", None)
                fallback_config.pop("response_schema", None)
                fallback_request["config"] = fallback_config
                response = call_with_schema_fallback(
                    self.client.models.generate_content,
                    request,
                    fallback_request,
                )
            else:
                response = self.client.models.generate_content(**request)
            return Response(text=response.text or "", usage=self._usage(response))
        except Exception as e:
            raise map_provider_exception(e, "Google", "API") from e

    def _send_request_stream(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        try:
            contents, request = self._request_args(messages, config)
            if not contents:
                return

            chunks = self.client.models.generate_content_stream(**request)
            try:
                for chunk in chunks:
                    if chunk.text:
                        yield chunk.text
            finally:
                close = getattr(chunks, "close", None)
                if callable(close):
                    close()
        except Exception as e:
            raise map_provider_exception(e, "Google", "streaming") from e

    def _send_request_stream_events(self, messages, config):
        try:
            contents, request = self._request_args(messages, config)
            if not contents:
                return

            chunks = self.client.models.generate_content_stream(**request)
            index = 0
            try:
                for chunk in chunks:
                    if chunk.text:
                        yield TextDelta(text=chunk.text, index=index)
                        index += 1
                    usage = self._usage(chunk)
                    if usage is not None:
                        yield UsageUpdate(**usage.__dict__)
            finally:
                close = getattr(chunks, "close", None)
                if callable(close):
                    close()
        except Exception as e:
            raise map_provider_exception(e, "Google", "streaming") from e

    # ─── Async ─────────────────────────────────────────────

    async def _send_request_async(
        self,
        messages: list[dict[str, str]],
        config: AdvancedConfig,
        output_type: str = None,
    ) -> Response:
        self._check_async_client_loop()
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError("Google provider currently supports text generation primarily.")

        try:
            contents, request = self._request_args(messages, config)
            if not contents:
                return Response(text="")

            response_model = config.extra.get("response_model")
            schema = strict_json_schema(response_model) if response_model is not None else None
            if schema is not None:
                fallback_request = dict(request)
                fallback_config = dict(request["config"])
                fallback_config.pop("response_mime_type", None)
                fallback_config.pop("response_schema", None)
                fallback_request["config"] = fallback_config
                response = await call_with_schema_fallback_async(
                    self.client.aio.models.generate_content,
                    request,
                    fallback_request,
                )
            else:
                response = await self.client.aio.models.generate_content(**request)
            return Response(text=response.text or "", usage=self._usage(response))
        except Exception as e:
            raise map_provider_exception(e, "Google", "API") from e

    async def _send_request_stream_async(self, messages, config) -> AsyncIterator[str]:
        self._check_async_client_loop()
        try:
            contents, request = self._request_args(messages, config)
            if not contents:
                return

            chunks = self.client.aio.models.generate_content_stream(**request)
            try:
                async for chunk in chunks:
                    if chunk.text:
                        yield chunk.text
            finally:
                close = getattr(chunks, "aclose", None)
                if callable(close):
                    await close()
        except Exception as e:
            raise map_provider_exception(e, "Google", "streaming") from e

    async def _send_request_stream_events_async(self, messages, config) -> AsyncIterator:
        self._check_async_client_loop()
        try:
            contents, request = self._request_args(messages, config)
            if not contents:
                return

            chunks = self.client.aio.models.generate_content_stream(**request)
            index = 0
            try:
                async for chunk in chunks:
                    if chunk.text:
                        yield TextDelta(text=chunk.text, index=index)
                        index += 1
                    usage = self._usage(chunk)
                    if usage is not None:
                        yield UsageUpdate(**usage.__dict__)
            finally:
                close = getattr(chunks, "aclose", None)
                if callable(close):
                    await close()
        except Exception as e:
            raise map_provider_exception(e, "Google", "streaming") from e
