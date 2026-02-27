import os
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError
from .openai_provider import OpenAIProvider


class AzureProvider(OpenAIProvider):
    def __init__(self, api_key: str = None, model: str = None, endpoint: str = None,
                 api_version: str = None, deployment_name: str = None, **kwargs):

        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        if not self.api_key:
            raise APIKeyError("Azure API Key is missing. Set AZURE_OPENAI_API_KEY env var or pass api_key=")

        self.endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not self.endpoint:
            raise ProviderError("Azure Endpoint is missing. Set AZURE_OPENAI_ENDPOINT env var or pass endpoint=")

        self.api_version = api_version or os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

        # Initialize the AzureOpenAI client
        import openai
        self.client = openai.AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )

        self.model = model or deployment_name or os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        if not self.model:
            # Azure uses "deployment name" as model parameter usually.
            raise ProviderError("Azure Model (Deployment Name) is missing. "
                                "Set AZURE_OPENAI_DEPLOYMENT_NAME env var or pass model=")

        self.persona = None
        self.config = AdvancedConfig(**kwargs)

    def _get_api_key_env_var(self):
        return "AZURE_OPENAI_API_KEY"

    def _get_default_model(self):
        return None  # Must be provided for Azure as it's deployment specific

    # Inherits _send_request from OpenAIProvider as AzureOpenAI client is compatible with OpenAI client methods.
    # verify _generate_image compatibility?
    # Azure DALL-E 3 works similarly.
    # Azure TTS/STT works similarly but might need deployment names.
    # Assuming standard compatibility for now.
