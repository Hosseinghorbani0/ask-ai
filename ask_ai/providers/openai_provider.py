import json
import logging
from collections.abc import AsyncIterator, Iterator

try:
    import openai
except ImportError:
    openai = None

from ..base import BaseProvider, Response
from ..capabilities import Capabilities
from ..config import AdvancedConfig
from ..events import TextDelta, UsageUpdate
from ..exceptions import APIKeyError, ProviderError, map_provider_exception
from ..media import AudioObject, ImageObject
from ..observability import usage_from_fields
from ..structured import (
    call_with_schema_fallback,
    call_with_schema_fallback_async,
    strict_json_schema,
    structured_output_name,
)

logger = logging.getLogger("ask_ai")


class OpenAIProvider(BaseProvider):
    def capabilities(self) -> Capabilities:
        return Capabilities(
            streaming=True,
            async_streaming=True,
            structured_output=True,
            tool_calls=True,
            image_generation=True,
            audio_generation=True,
            vision=True,
        )

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("OpenAI API Key is missing. Set OPENAI_API_KEY env var or pass api_key=")

        if openai is None:
            raise ProviderError("OpenAI client library not installed. Run: pip install openai")

        self.client = openai.OpenAI(
            api_key=self.api_key,
            timeout=self.config.extra.get("timeout", 30.0),
            max_retries=0,
        )
        self._async_client = None  # Lazy-loaded

    @property
    def async_client(self):
        """Lazy-load the async client only when needed."""
        if self._async_client is None:
            self._async_client = openai.AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.config.extra.get("timeout", 30.0),
                max_retries=0,
            )
        return self._async_client

    def _get_api_key_env_var(self):
        return "OPENAI_API_KEY"

    def _get_default_model(self):
        return "gpt-4o"

    # ─── Sync ──────────────────────────────────────────────

    def _send_request(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        # Explicit media
        if output_type == "image":
            return self._generate_image(messages, config)
        if output_type == "audio":
            return self._generate_audio(messages, config)

        # Text / Smart Intent
        return self._generate_text_or_smart(messages, config)

    def _generate_text_or_smart(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Response:
        try:
            response_model = config.extra.get("response_model")
            native_kwargs = self._build_chat_kwargs(
                messages, config, include_tools=response_model is None
            )
            fallback_kwargs = dict(native_kwargs)
            if "response_format" in native_kwargs:
                fallback_kwargs.pop("response_format")
                response = call_with_schema_fallback(
                    self.client.chat.completions.create,
                    native_kwargs,
                    fallback_kwargs,
                )
            else:
                response = self.client.chat.completions.create(**native_kwargs)
            result = self._process_chat_response(response, messages, config)
            result.usage = usage_from_fields(
                getattr(response, "usage", None), "prompt_tokens", "completion_tokens", "total_tokens"
            )
            return result
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "API") from e

    def _send_request_stream(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        """Sync streaming — yields text chunks."""
        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=False)
            kwargs["stream"] = True
            stream = self.client.chat.completions.create(**kwargs)

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "streaming") from e

    def _send_request_stream_events(self, messages, config):
        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=False)
            kwargs["stream"] = True
            kwargs["stream_options"] = {"include_usage": True}
            stream = self.client.chat.completions.create(**kwargs)
            index = 0
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield TextDelta(text=chunk.choices[0].delta.content, index=index)
                    index += 1
                usage = usage_from_fields(
                    getattr(chunk, "usage", None),
                    "prompt_tokens",
                    "completion_tokens",
                    "total_tokens",
                )
                if usage is not None:
                    yield UsageUpdate(**usage.__dict__)
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "streaming") from e

    # ─── Async ─────────────────────────────────────────────

    async def _send_request_async(self, messages: list[dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type == "image":
            return await self._generate_image_async(messages, config)
        if output_type == "audio":
            return await self._generate_audio_async(messages, config)

        try:
            response_model = config.extra.get("response_model")
            native_kwargs = self._build_chat_kwargs(
                messages, config, include_tools=response_model is None
            )
            fallback_kwargs = dict(native_kwargs)
            if "response_format" in native_kwargs:
                fallback_kwargs.pop("response_format")
                response = await call_with_schema_fallback_async(
                    self.async_client.chat.completions.create,
                    native_kwargs,
                    fallback_kwargs,
                )
            else:
                response = await self.async_client.chat.completions.create(**native_kwargs)
            result = await self._process_chat_response_async(response, messages, config)
            result.usage = usage_from_fields(
                getattr(response, "usage", None), "prompt_tokens", "completion_tokens", "total_tokens"
            )
            return result
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "API") from e

    async def _send_request_stream_async(self, messages: list[dict[str, str]], config: AdvancedConfig) -> AsyncIterator[str]:
        """Async streaming — yields text chunks."""
        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=False)
            kwargs["stream"] = True
            stream = await self.async_client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "streaming") from e

    async def _send_request_stream_events_async(self, messages, config):
        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=False)
            kwargs["stream"] = True
            kwargs["stream_options"] = {"include_usage": True}
            stream = await self.async_client.chat.completions.create(**kwargs)
            index = 0
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield TextDelta(text=chunk.choices[0].delta.content, index=index)
                    index += 1
                usage = usage_from_fields(
                    getattr(chunk, "usage", None),
                    "prompt_tokens",
                    "completion_tokens",
                    "total_tokens",
                )
                if usage is not None:
                    yield UsageUpdate(**usage.__dict__)
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "streaming") from e

    # ─── Helpers ───────────────────────────────────────────

    def _build_chat_kwargs(self, messages: list[dict[str, str]], config: AdvancedConfig, include_tools: bool = False) -> dict:
        """Build kwargs for chat.completions.create, filtering None values."""
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

        if include_tools:
            tools = self._get_media_tools()
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

        response_model = config.extra.get("response_model")
        schema = strict_json_schema(response_model) if response_model is not None else None
        if schema is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": structured_output_name(response_model),
                    "strict": True,
                    "schema": schema,
                },
            }

        # Filter None values
        return {k: v for k, v in kwargs.items() if v is not None}

    def _process_chat_response(self, response, messages, config) -> Response:
        """Process a chat completion response, handling tool calls."""
        message = response.choices[0].message

        # Check for tool calls (Smart Intent)
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "generate_image":
                logger.info("Smart Intent: Image generation detected")
                return self._generate_image(
                    [{"role": "user", "content": arguments.get("prompt")}], config
                )
            elif function_name == "generate_speech":
                logger.info("Smart Intent: Speech generation detected")
                return self._generate_audio(
                    [{"role": "user", "content": arguments.get("text")}], config
                )

        return Response(text=message.content or "")

    async def _process_chat_response_async(self, response, messages, config) -> Response:
        """Process a chat response without blocking the async event loop."""
        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "generate_image":
                logger.info("Smart Intent: Image generation detected")
                return await self._generate_image_async(
                    [{"role": "user", "content": arguments.get("prompt")}], config
                )
            if function_name == "generate_speech":
                logger.info("Smart Intent: Speech generation detected")
                return await self._generate_audio_async(
                    [{"role": "user", "content": arguments.get("text")}], config
                )

        return Response(text=message.content or "")

    # ─── Image Generation ──────────────────────────────────

    def _generate_image(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Response:
        prompt = messages[-1]["content"]
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url

            # Download image bytes with httpx (falls back to urllib)
            img_data = _download_bytes(image_url, config.extra.get("timeout", 30.0))

            return Response(
                text=f"Generated image for: {prompt}",
                media=ImageObject(img_data)
            )
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "image generation") from e

    async def _generate_image_async(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Response:
        prompt = messages[-1]["content"]
        try:
            response = await self.async_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            img_data = await _download_bytes_async(image_url, config.extra.get("timeout", 30.0))

            return Response(
                text=f"Generated image for: {prompt}",
                media=ImageObject(img_data)
            )
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "image generation") from e

    # ─── Audio Generation ──────────────────────────────────

    def _generate_audio(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Response:
        text = messages[-1]["content"]
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
                timeout=config.extra.get("timeout"),
            )
            return Response(
                text=f"Generated audio for: {text}",
                media=AudioObject(response.content)
            )
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "audio generation") from e

    async def _generate_audio_async(self, messages: list[dict[str, str]], config: AdvancedConfig) -> Response:
        text = messages[-1]["content"]
        try:
            response = await self.async_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
                timeout=config.extra.get("timeout"),
            )
            return Response(
                text=f"Generated audio for: {text}",
                media=AudioObject(response.content)
            )
        except Exception as e:
            raise map_provider_exception(e, "OpenAI", "audio generation") from e


# ─── Download Helpers ──────────────────────────────────────

def _download_bytes(url: str, timeout: float = 30.0) -> bytes:
    from ..media_security import MediaPolicy, download_media
    return download_media(url, MediaPolicy(timeout=timeout))


async def _download_bytes_async(url: str, timeout: float = 30.0) -> bytes:
    import asyncio

    from ..media_security import MediaPolicy, download_media
    return await asyncio.get_running_loop().run_in_executor(
        None, download_media, url, MediaPolicy(timeout=timeout)
    )
