import os
from typing import List, Dict, Any

try:
    import openai
except ImportError:
    openai = None

from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError
from .openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter provider — routes to multiple models via OpenAI-compatible API."""

    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        if openai is None:
            raise ProviderError("OpenAI client library not installed. Run: pip install openai")

        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise APIKeyError("OpenRouter API Key is missing. Set OPENROUTER_API_KEY env var or pass api_key=")

        # Sync client with OpenRouter base URL
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self._async_client = None

        self.model = model or "openai/gpt-4o"
        self.persona = None
        self.config = AdvancedConfig(**kwargs)

    @property
    def async_client(self):
        """Lazy-load async client for OpenRouter."""
        if self._async_client is None:
            self._async_client = openai.AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
        return self._async_client

    def _get_api_key_env_var(self):
        return "OPENROUTER_API_KEY"

    def _get_default_model(self):
        return "openai/gpt-4o"

    def _get_media_tools(self) -> List[Dict[str, Any]]:
        # OpenRouter does not support media endpoints
        return []

    def _generate_image(self, messages, config):
        raise ProviderError("OpenRouter does not support Image Generation via this library.")

    def _generate_audio(self, messages, config):
        raise ProviderError("OpenRouter does not support Audio Generation via this library.")

    async def _generate_image_async(self, messages, config):
        raise ProviderError("OpenRouter does not support Image Generation via this library.")

    async def _generate_audio_async(self, messages, config):
        raise ProviderError("OpenRouter does not support Audio Generation via this library.")
