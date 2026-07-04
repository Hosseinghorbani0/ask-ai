import json
import logging
from typing import List, Dict, Iterator, AsyncIterator

try:
    import openai
except ImportError:
    openai = None

from ..base import BaseProvider, Response
from ..media import ImageObject, AudioObject
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError

logger = logging.getLogger("ask_ai")


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("OpenAI API Key is missing. Set OPENAI_API_KEY env var or pass api_key=")

        if openai is None:
            raise ProviderError("OpenAI client library not installed. Run: pip install openai")

        self.client = openai.OpenAI(api_key=self.api_key)
        self._async_client = None  # Lazy-loaded

    @property
    def async_client(self):
        """Lazy-load the async client only when needed."""
        if self._async_client is None:
            self._async_client = openai.AsyncOpenAI(api_key=self.api_key)
        return self._async_client

    def _get_api_key_env_var(self):
        return "OPENAI_API_KEY"

    def _get_default_model(self):
        return "gpt-4o"

    # ─── Sync ──────────────────────────────────────────────

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        # Explicit media
        if output_type == "image":
            return self._generate_image(messages, config)
        if output_type == "audio":
            return self._generate_audio(messages, config)

        # Text / Smart Intent
        return self._generate_text_or_smart(messages, config)

    def _generate_text_or_smart(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=True)
            response = self.client.chat.completions.create(**kwargs)
            return self._process_chat_response(response, messages, config)
        except Exception as e:
            raise ProviderError(f"OpenAI API Error: {e}") from e

    def _send_request_stream(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        """Sync streaming — yields text chunks."""
        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=False)
            kwargs["stream"] = True
            stream = self.client.chat.completions.create(**kwargs)

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise ProviderError(f"OpenAI Streaming Error: {e}") from e

    # ─── Async ─────────────────────────────────────────────

    async def _send_request_async(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type == "image":
            return await self._generate_image_async(messages, config)
        if output_type == "audio":
            return await self._generate_audio_async(messages, config)

        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=True)
            response = await self.async_client.chat.completions.create(**kwargs)
            return self._process_chat_response(response, messages, config)
        except Exception as e:
            raise ProviderError(f"OpenAI API Error: {e}") from e

    async def _send_request_stream_async(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> AsyncIterator[str]:
        """Async streaming — yields text chunks."""
        try:
            kwargs = self._build_chat_kwargs(messages, config, include_tools=False)
            kwargs["stream"] = True
            stream = await self.async_client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise ProviderError(f"OpenAI Streaming Error: {e}") from e

    # ─── Helpers ───────────────────────────────────────────

    def _build_chat_kwargs(self, messages: List[Dict[str, str]], config: AdvancedConfig, include_tools: bool = False) -> dict:
        """Build kwargs for chat.completions.create, filtering None values."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
        }
        if config.stop:
            kwargs["stop"] = config.stop

        if include_tools:
            tools = self._get_media_tools()
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

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

    # ─── Image Generation ──────────────────────────────────

    def _generate_image(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
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
            img_data = _download_bytes(image_url)

            return Response(
                text=f"Generated image for: {prompt}",
                media=ImageObject(img_data)
            )
        except Exception as e:
            raise ProviderError(f"OpenAI Image Error: {e}") from e

    async def _generate_image_async(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
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
            img_data = await _download_bytes_async(image_url)

            return Response(
                text=f"Generated image for: {prompt}",
                media=ImageObject(img_data)
            )
        except Exception as e:
            raise ProviderError(f"OpenAI Image Error: {e}") from e

    # ─── Audio Generation ──────────────────────────────────

    def _generate_audio(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
        text = messages[-1]["content"]
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            return Response(
                text=f"Generated audio for: {text}",
                media=AudioObject(response.content)
            )
        except Exception as e:
            raise ProviderError(f"OpenAI Audio Error: {e}") from e

    async def _generate_audio_async(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
        text = messages[-1]["content"]
        try:
            response = await self.async_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            return Response(
                text=f"Generated audio for: {text}",
                media=AudioObject(response.content)
            )
        except Exception as e:
            raise ProviderError(f"OpenAI Audio Error: {e}") from e


# ─── Download Helpers ──────────────────────────────────────

def _download_bytes(url: str) -> bytes:
    """Download bytes from URL. Uses httpx if available, falls back to urllib."""
    try:
        import httpx
        with httpx.Client(timeout=30) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.content
    except ImportError:
        from urllib.request import urlopen
        with urlopen(url, timeout=30) as resp:
            return resp.read()


async def _download_bytes_async(url: str) -> bytes:
    """Async download bytes from URL."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
    except ImportError:
        import asyncio
        return await asyncio.get_running_loop().run_in_executor(None, _download_bytes, url)
