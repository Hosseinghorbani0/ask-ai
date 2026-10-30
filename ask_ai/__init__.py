"""
ask-ai: A minimal Python SDK to switch between LLM providers in one line.
"""

__version__ = "0.4.3"

from .base import Response
from .config import AdvancedConfig
from .exceptions import (
    AskAIConfigError,
    AskAIError,
    AskAINetworkError,
    AskAIParsingError,
    AskAIRateLimitError,
    MediaTypeNotSupportedError,
    ProviderAuthError,
    ProviderError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    StreamNotSupportedError,
)
from .media import AudioObject, ImageObject
from .providers import Anthropic, Azure, Google, Groq, OpenAI, OpenRouter

__all__ = [
    # Providers
    "OpenAI",
    "Anthropic",
    "Google",
    "Groq",
    "Azure",
    "OpenRouter",
    # Core
    "AdvancedConfig",
    "Response",
    "ImageObject",
    "AudioObject",
    # Exceptions
    "AskAIError",
    "AskAIConfigError",
    "AskAINetworkError",
    "AskAIRateLimitError",
    "AskAIParsingError",
    "ProviderError",
    "ProviderAuthError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    "ProviderInvalidRequestError",
    "ProviderUnavailableError",
    "MediaTypeNotSupportedError",
    "StreamNotSupportedError",
]
