class AskAIError(Exception):
    """Base exception for all ask-ai errors."""
    pass

class AskAIConfigError(AskAIError):
    """Raised when configuration (like API keys) is missing or invalid."""
    pass

class AskAINetworkError(AskAIError):
    """Raised when a network connection fails (timeout, disconnect)."""
    pass

class AskAIRateLimitError(AskAIError):
    """Raised when the provider rate limits the request (429)."""
    pass

class ProviderError(AskAIError):
    """Raised when the provider API fails (e.g. 500 error or bad request)."""
    pass

class MediaTypeNotSupportedError(AskAIError):
    """Raised when a provider can't handle the requested media type."""
    pass

class AskAIParsingError(AskAIError):
    """Raised when expect_json is True but the response cannot be parsed."""
    pass

# Alias for backwards compatibility internally
APIKeyError = AskAIConfigError
