import asyncio
import logging
from typing import List, Dict, Iterator, AsyncIterator

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..base import BaseProvider, Response
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError, MediaTypeNotSupportedError

logger = logging.getLogger("ask_ai")


class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("Google API Key is missing. Set GOOGLE_API_KEY env var or pass api_key=")

        if genai is None:
            raise ProviderError("Google Generative AI library not installed. Run: pip install google-generativeai")

        # Configure per-instance (still uses global genai.configure, but we store for reference)
        genai.configure(api_key=self.api_key)
        self.model_name = self.model

    def _get_api_key_env_var(self):
        return "GOOGLE_API_KEY"

    def _get_default_model(self):
        return "gemini-2.0-flash"

    # ─── Helpers ───────────────────────────────────────────

    def _convert_messages(self, messages: List[Dict[str, str]]):
        """Convert OpenAI-style messages to Gemini format."""
        gemini_messages = []
        system_instruction = None

        for m in messages:
            role = m["role"]
            content = m["content"]
            if role == "system":
                system_instruction = content
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})

        return gemini_messages, system_instruction

    def _build_generation_config(self, config: AdvancedConfig):
        """Build Gemini GenerationConfig."""
        return genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
        )

    def _create_model(self, system_instruction=None):
        """Create a GenerativeModel instance."""
        return genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction
        )

    # ─── Sync ──────────────────────────────────────────────

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError("Google provider currently supports text generation primarily.")

        try:
            gemini_messages, system_instruction = self._convert_messages(messages)
            generation_config = self._build_generation_config(config)
            model = self._create_model(system_instruction)

            if not gemini_messages:
                return Response(text="")

            last_msg = gemini_messages[-1]
            history = gemini_messages[:-1]

            chat = model.start_chat(history=history)
            response = chat.send_message(last_msg["parts"][0], generation_config=generation_config)

            return Response(text=response.text)
        except Exception as e:
            raise ProviderError(f"Google API Error: {e}") from e

    def _send_request_stream(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        """Sync streaming with Gemini."""
        try:
            gemini_messages, system_instruction = self._convert_messages(messages)
            generation_config = self._build_generation_config(config)
            model = self._create_model(system_instruction)

            if not gemini_messages:
                return

            last_msg = gemini_messages[-1]
            history = gemini_messages[:-1]

            chat = model.start_chat(history=history)
            response = chat.send_message(
                last_msg["parts"][0],
                generation_config=generation_config,
                stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise ProviderError(f"Google Streaming Error: {e}") from e

    # ─── Async ─────────────────────────────────────────────

    async def _send_request_async(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        if output_type in ("image", "audio"):
            raise MediaTypeNotSupportedError("Google provider currently supports text generation primarily.")

        try:
            gemini_messages, system_instruction = self._convert_messages(messages)
            generation_config = self._build_generation_config(config)
            model = self._create_model(system_instruction)

            if not gemini_messages:
                return Response(text="")

            last_msg = gemini_messages[-1]
            history = gemini_messages[:-1]

            chat = model.start_chat(history=history)

            # google-generativeai uses sync API, wrap in executor
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: chat.send_message(last_msg["parts"][0], generation_config=generation_config)
            )

            return Response(text=response.text)
        except Exception as e:
            raise ProviderError(f"Google API Error: {e}") from e
