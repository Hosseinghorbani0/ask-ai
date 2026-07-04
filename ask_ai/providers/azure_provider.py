import os

try:
    import openai
except ImportError:
    openai = None

from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError
from .openai_provider import OpenAIProvider


class AzureProvider(OpenAIProvider):
    """Azure OpenAI provider. Inherits all functionality from OpenAIProvider."""

    def __init__(self, api_key: str = None, model: str = None, endpoint: str = None,
                 api_version: str = None, deployment_name: str = None, **kwargs):

        if openai is None:
            raise ProviderError("OpenAI client library not installed. Run: pip install openai")

        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        if not self.api_key:
            raise APIKeyError("Azure API Key is missing. Set AZURE_OPENAI_API_KEY env var or pass api_key=")

        self.endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not self.endpoint:
            raise ProviderError("Azure Endpoint is missing. Set AZURE_OPENAI_ENDPOINT env var or pass endpoint=")

        self.api_version = api_version or os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01")

        # Initialize sync client
        self.client = openai.AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        self._async_client = None

        self.model = model or deployment_name or os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        if not self.model:
            raise ProviderError(
                "Azure Model (Deployment Name) is missing. "
                "Set AZURE_OPENAI_DEPLOYMENT_NAME env var or pass model="
            )

        self.persona = None
        self.config = AdvancedConfig(**kwargs)

    @property
    def async_client(self):
        """Lazy-load the async Azure OpenAI client."""
        if self._async_client is None:
            self._async_client = openai.AsyncAzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        return self._async_client

    def _get_api_key_env_var(self):
        return "AZURE_OPENAI_API_KEY"

    def _get_default_model(self):
        return None  # Must be provided — deployment-specific

    # Inherits all sync/async/streaming methods from OpenAIProvider
