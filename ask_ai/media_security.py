from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from .exceptions import MediaSecurityError


@dataclass(frozen=True)
class MediaPolicy:
    max_bytes: int = 25 * 1024 * 1024
    allowed_mime_types: Optional[set[str]] = None
    allowed_hosts: Optional[set[str]] = None
    timeout: float = 30.0

    def validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise MediaSecurityError("Media URLs must use HTTPS and include a hostname.")
        if self.allowed_hosts is not None and parsed.hostname not in self.allowed_hosts:
            raise MediaSecurityError(f"Media host is not allowlisted: {parsed.hostname}")

    def validate_mime(self, mime_type: str) -> None:
        if self.allowed_mime_types and mime_type not in self.allowed_mime_types:
            raise MediaSecurityError(f"Media MIME type is not allowed: {mime_type}")


def download_media(url: str, policy: Optional[MediaPolicy] = None) -> bytes:
    """Stream media bytes with URL, MIME, size, and timeout validation."""
    policy = policy or MediaPolicy()
    policy.validate_url(url)
    try:
        import httpx
    except ImportError as error:
        raise MediaSecurityError("httpx is required for secure media downloads.") from error

    try:
        with httpx.Client(timeout=policy.timeout, follow_redirects=False) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").split(";", 1)[0].strip()
                policy.validate_mime(content_type)
                length = response.headers.get("content-length")
                if length and int(length) > policy.max_bytes:
                    raise MediaSecurityError("Media payload exceeds the configured size limit.")
                chunks = []
                total = 0
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > policy.max_bytes:
                        raise MediaSecurityError("Media payload exceeds the configured size limit.")
                    chunks.append(chunk)
                return b"".join(chunks)
    except MediaSecurityError:
        raise
    except Exception as error:
        raise MediaSecurityError(f"Secure media download failed: {error}") from error
