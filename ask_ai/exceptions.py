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


class ProviderAuthError(ProviderError):
    """Raised when provider authentication fails."""
    pass


class ProviderRateLimitError(AskAIRateLimitError, ProviderError):
    """Raised when a provider rate-limits a request."""
    pass


class ProviderTimeoutError(AskAINetworkError, ProviderError):
    """Raised when a provider request times out."""
    pass


class ProviderInvalidRequestError(ProviderError):
    """Raised when a provider rejects request parameters."""
    pass


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is temporarily unavailable."""
    pass


class MediaTypeNotSupportedError(AskAIError):
    """Raised when a provider can't handle the requested media type."""
    pass


class AskAIParsingError(AskAIError):
    """Raised when expect_json is True but the response cannot be parsed."""
    pass


class StructuredValidationError(AskAIParsingError):
    """Raised when structured output does not match the requested schema."""
    pass


class StreamNotSupportedError(AskAIError):
    """Raised when streaming is requested but the provider doesn't support it."""
    pass


# Alias for backwards compatibility
APIKeyError = AskAIConfigError


def map_provider_exception(error: Exception, provider: str, operation: str = "request") -> ProviderError:
    """Map SDK-specific exceptions to stable ask-ai provider exceptions."""
    status_code = getattr(error, "status_code", None)
    if status_code is None:
        response = getattr(error, "response", None)
        status_code = getattr(response, "status_code", None)

    error_text = str(error).lower()
    error_name = error.__class__.__name__.lower()
    prefix = f"{provider} {operation} failed"

    if status_code in (401, 403) or any(
        marker in error_name or marker in error_text
        for marker in ("authentication", "autherror", "invalid api key", "unauthorized", "forbidden")
    ):
        return ProviderAuthError(f"{prefix}: {error}")
    if status_code == 429 or any(
        marker in error_name or marker in error_text
        for marker in ("ratelimit", "rate_limit", "rate limit", "too many requests")
    ):
        return ProviderRateLimitError(f"{prefix}: {error}")
    if any(
        marker in error_name or marker in error_text
        for marker in ("timeout", "timed out", "connecterror", "connectionerror", "connection reset")
    ):
        return ProviderTimeoutError(f"{prefix}: {error}")
    if isinstance(status_code, int) and status_code >= 500:
        return ProviderUnavailableError(f"{prefix}: {error}")
    if status_code in (400, 404, 422) or any(
        marker in error_name or marker in error_text
        for marker in ("badrequest", "invalid request", "validationerror", "unprocessable")
    ):
        return ProviderInvalidRequestError(f"{prefix}: {error}")
    return ProviderError(f"{prefix}: {error}")
