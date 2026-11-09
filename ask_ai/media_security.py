import ipaddress
import socket
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from .exceptions import MediaSecurityError
from .media import HeaderInspector


@dataclass(frozen=True)
class MediaPolicy:
    max_bytes: int = 25 * 1024 * 1024
    allowed_mime_types: Optional[set[str]] = None
    allowed_hosts: Optional[set[str]] = None
    timeout: float = 30.0
    allow_private: bool = False

    def _validated_addresses(self, url: str) -> tuple[str, list[str]]:
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or 443
        except ValueError as error:
            raise MediaSecurityError("Media URL is malformed.") from error
        if parsed.scheme != "https" or not hostname:
            raise MediaSecurityError("Media URLs must use HTTPS and include a hostname.")
        if parsed.username is not None or parsed.password is not None:
            raise MediaSecurityError("Media URLs must not contain embedded credentials.")
        hostname = _normalize_hostname(hostname)
        if self.allowed_hosts is not None:
            allowed_hosts = {_normalize_hostname(host) for host in self.allowed_hosts}
            if hostname not in allowed_hosts:
                raise MediaSecurityError(f"Media host is not allowlisted: {hostname}")
        try:
            addresses = [ipaddress.ip_address(hostname)]
        except ValueError:
            try:
                address_info = socket.getaddrinfo(
                    hostname, port, type=socket.SOCK_STREAM
                )
            except OSError as error:
                raise MediaSecurityError(
                    f"Unable to resolve media host: {hostname}"
                ) from error
            addresses = [
                ipaddress.ip_address(result[4][0].split("%", 1)[0])
                for result in address_info
            ]
        if not addresses:
            raise MediaSecurityError(f"Media host resolved to no addresses: {hostname}")
        if not self.allow_private:
            for address in addresses:
                if (
                    address.is_private
                    or address.is_loopback
                    or address.is_link_local
                    or address.is_reserved
                    or address.is_multicast
                    or address.is_unspecified
                    or not address.is_global
                ):
                    raise MediaSecurityError(
                        f"Media host resolves to a non-public IP address: {address}"
                    )
        return hostname, [str(address) for address in addresses]

    def validate_url(self, url: str) -> None:
        self._validated_addresses(url)

    def validate_mime(self, mime_type: str) -> None:
        if self.allowed_mime_types and mime_type not in self.allowed_mime_types:
            raise MediaSecurityError(f"Media MIME type is not allowed: {mime_type}")


def download_media(url: str, policy: Optional[MediaPolicy] = None) -> bytes:
    """Stream media bytes with URL, MIME, size, and timeout validation."""
    policy = policy or MediaPolicy()
    hostname, addresses = policy._validated_addresses(url)
    try:
        import httpx
    except ImportError as error:
        raise MediaSecurityError("httpx is required for secure media downloads.") from error

    try:
        transport = _create_pinned_transport(httpx, hostname, addresses)
        with httpx.Client(
            timeout=policy.timeout,
            follow_redirects=False,
            transport=transport,
        ) as client:
            with client.stream("GET", url) as response:
                if 300 <= response.status_code < 400:
                    raise MediaSecurityError(
                        "Media redirects are disabled; use a final HTTPS URL on an allowlisted host."
                    )
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").split(";", 1)[0].strip()
                policy.validate_mime(content_type)
                length = response.headers.get("content-length")
                content_length = None
                if length is not None:
                    try:
                        content_length = int(length)
                    except (TypeError, ValueError) as error:
                        raise MediaSecurityError(
                            "Media response has an invalid Content-Length."
                        ) from error
                    if content_length < 0:
                        raise MediaSecurityError(
                            "Media response has an invalid Content-Length."
                        )
                    if content_length > policy.max_bytes:
                        raise MediaSecurityError(
                            "Media payload exceeds the configured size limit."
                        )
                chunks = []
                total = 0
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > policy.max_bytes:
                        raise MediaSecurityError("Media payload exceeds the configured size limit.")
                    chunks.append(chunk)
                content_encoding = response.headers.get(
                    "content-encoding", "identity"
                ).lower()
                if (
                    content_length is not None
                    and content_encoding in {"", "identity"}
                    and content_length != total
                ):
                    raise MediaSecurityError(
                        "Media Content-Length does not match the streamed payload size."
                    )
                data = b"".join(chunks)
                _, _, detected_mime = HeaderInspector.detect_type(data)
                if policy.allowed_mime_types and detected_mime not in policy.allowed_mime_types:
                    raise MediaSecurityError(
                        f"Detected media MIME type is not allowed: {detected_mime}"
                    )
                if content_type and detected_mime != content_type:
                    raise MediaSecurityError(
                        f"Media MIME header {content_type!r} conflicts with detected type {detected_mime!r}."
                    )
                return data
    except MediaSecurityError:
        raise
    except Exception as error:
        raise MediaSecurityError(f"Secure media download failed: {error}") from error


def _normalize_hostname(hostname: str) -> str:
    try:
        return hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as error:
        raise MediaSecurityError("Media URL contains an invalid hostname.") from error


def _create_pinned_transport(httpx, hostname: str, addresses: list[str]):
    import httpcore

    normalized_hostname = hostname.encode("idna").decode("ascii").lower().rstrip(".")

    class PinnedNetworkBackend(httpcore.SyncBackend):
        def connect_tcp(
            self,
            host,
            port,
            timeout=None,
            local_address=None,
            socket_options=None,
        ):
            if host.lower().rstrip(".") != normalized_hostname:
                raise httpcore.ConnectError(
                    "Media transport attempted to connect to an unvalidated host."
                )

            last_error = None
            for address in addresses:
                try:
                    return super().connect_tcp(
                        address,
                        port,
                        timeout=timeout,
                        local_address=local_address,
                        socket_options=socket_options,
                    )
                except (httpcore.ConnectError, httpcore.ConnectTimeout) as error:
                    last_error = error
            raise last_error

    transport = httpx.HTTPTransport()
    transport._pool._network_backend = PinnedNetworkBackend()
    return transport
