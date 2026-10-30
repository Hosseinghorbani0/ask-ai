"""
ask-ai: A minimal Python SDK to switch between LLM providers in one line.
"""

__version__ = "0.4.3"

from .base import Response
from .capabilities import Capabilities
from .config import AdvancedConfig
from .events import Completed, Error, TextDelta, ToolCall, UsageUpdate
from .exceptions import (
    AskAIConfigError,
    AskAIError,
    AskAINetworkError,
    AskAIParsingError,
    AskAIRateLimitError,
    MediaSecurityError,
    MediaTypeNotSupportedError,
    ProviderAuthError,
    ProviderError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    StreamNotSupportedError,
    StructuredValidationError,
)
from .media import AudioObject, ImageObject
from .media_security import MediaPolicy, download_media
from .observability import Observability, ResponseMetadata, Usage
from .providers import Anthropic, Azure, Google, Groq, OpenAI, OpenRouter
from .router import Router
from .session import ConversationSession
from .structured import parse_structured

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
    "MediaSecurityError",
    "StreamNotSupportedError",
    "StructuredValidationError",
    "parse_structured",
    "TextDelta",
    "ToolCall",
    "UsageUpdate",
    "Completed",
    "Error",
    "Observability",
    "ResponseMetadata",
    "Usage",
    "Capabilities",
    "Router",
    "ConversationSession",
    "MediaPolicy",
    "download_media",
]
