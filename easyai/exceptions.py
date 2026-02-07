class EasyAIError(Exception):
    """Base exception for all easyai errors."""
    pass

class APIKeyError(EasyAIError):
    """Raised when API key is missing or invalid."""
    pass

class ProviderError(EasyAIError):
    """Raised when the provider API fails (e.g. 500 error)."""
    pass

class MediaTypeNotSupportedError(EasyAIError):
    """Raised when a provider can't handle the requested media type."""
    pass
