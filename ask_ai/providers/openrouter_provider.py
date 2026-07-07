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
        prompt = messages[-1]["content"]
        try:
            import httpx
        except ImportError:
            raise ProviderError("httpx client library is required for OpenRouter Image Generation. Run: pip install httpx")
        
        from ..media import ImageObject
        from .openai_provider import _download_bytes

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt
        }
        try:
            response = httpx.post("https://openrouter.ai/api/v1/images", json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            image_url = data["data"][0]["url"]
            img_data = _download_bytes(image_url)
            return Response(
                text=f"Generated image via OpenRouter ({self.model}) for: {prompt}",
                media=ImageObject(img_data)
            )
        except Exception as e:
            raise ProviderError(f"OpenRouter Image Generation Error: {e}") from e

    async def _generate_image_async(self, messages, config):
        prompt = messages[-1]["content"]
        try:
            import httpx
        except ImportError:
            raise ProviderError("httpx client library is required for OpenRouter Image Generation. Run: pip install httpx")

        from ..media import ImageObject
        from .openai_provider import _download_bytes_async

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("https://openrouter.ai/api/v1/images", json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                data = response.json()
            image_url = data["data"][0]["url"]
            img_data = await _download_bytes_async(image_url)
            return Response(
                text=f"Generated image via OpenRouter ({self.model}) for: {prompt}",
                media=ImageObject(img_data)
            )
        except Exception as e:
            raise ProviderError(f"OpenRouter Image Generation Error: {e}") from e

    def _generate_audio(self, messages, config):
        raise ProviderError("OpenRouter does not support Audio Generation via this library.")

    async def _generate_audio_async(self, messages, config):
        raise ProviderError("OpenRouter does not support Audio Generation via this library.")
