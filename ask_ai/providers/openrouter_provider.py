from typing import List, Dict, Any
import os
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError
from .openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        # Initialize OpenAIProvider but with OpenRouter base URL
        # We need to handle api_key lookup ourselves first or let OpenAIProvider do it?
        # OpenAIProvider looks for OPENAI_API_KEY. We want OPENROUTER_API_KEY.

        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise APIKeyError("OpenRouter API Key is missing. Set OPENROUTER_API_KEY env var or pass api_key=")

        # Initialize the OpenAI client with OpenRouter base URL
        import openai
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

        self.model = model or "openai/gpt-3.5-turbo"  # OpenRouter needs prefix usually? or just model name.
        self.persona = None
        self.config = AdvancedConfig(**kwargs)

    def _get_api_key_env_var(self):
        return "OPENROUTER_API_KEY"

    def _get_default_model(self):
        return "openai/gpt-3.5-turbo"

    def _get_media_tools(self) -> List[Dict[str, Any]]:
        # OpenRouter does not support standard OpenAI media endpoints (Image/Audio)
        # So we disable smart intent tools to prevent model from calling them.
        return []

    def _generate_image(self, messages, config):
        raise ProviderError("OpenRouter does not support Image Generation via this library yet.")

    def _generate_audio(self, messages, config):
        raise ProviderError("OpenRouter does not support Audio Generation via this library yet.")
