"""
ask-ai: A minimal Python SDK to switch between LLM providers in one line.
"""

__version__ = "0.4.0"

from .providers import (
    OpenAI,
    Anthropic,
    Google,
    Groq,
    Azure,
    OpenRouter
)
from .config import AdvancedConfig
from .base import Response
from .media import ImageObject, AudioObject
from .exceptions import (
    AskAIError,
    AskAIConfigError,
    AskAINetworkError,
    AskAIRateLimitError,
    AskAIParsingError,
    ProviderError,
    MediaTypeNotSupportedError,
    StreamNotSupportedError,
)

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
    "MediaTypeNotSupportedError",
    "StreamNotSupportedError",
]
