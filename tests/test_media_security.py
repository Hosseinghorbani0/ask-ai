import socket

import pytest

from ask_ai import MediaPolicy, download_media
from ask_ai.exceptions import MediaSecurityError
from ask_ai.media import ImageObject, MediaError


@pytest.fixture(autouse=True)
def mock_public_dns(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))
        ],
    )


def test_media_policy_rejects_insecure_and_unallowlisted_urls():
    policy = MediaPolicy(allowed_hosts={"example.com"})
    with pytest.raises(MediaSecurityError):
        policy.validate_url("http://example.com/image.png")
    with pytest.raises(MediaSecurityError):
        policy.validate_url("https://other.example/image.png")


def test_media_download_enforces_size_and_mime(monkeypatch):
    class Response:
        headers = {"content-type": "image/png", "content-length": "12"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def raise_for_status(self):
            return None

        def iter_bytes(self):
            yield b"123456"

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def stream(self, method, url):
            return Response()

    monkeypatch.setattr("httpx.Client", Client)
    with pytest.raises(MediaSecurityError):
        download_media("https://example.com/image.png", MediaPolicy(max_bytes=5))


def test_media_download_rejects_mime_spoofing(monkeypatch):
    class Response:
        status_code = 200
        headers = {"content-type": "image/png", "content-length": "12"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def raise_for_status(self):
            return None

        def iter_bytes(self):
            yield b"not-an-image"

    class Client:
        def __init__(self, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def stream(self, method, url):
            return Response()

    monkeypatch.setattr("httpx.Client", Client)
    with pytest.raises(MediaSecurityError, match="conflicts"):
        download_media(
            "https://example.com/image.png",
            MediaPolicy(
                allowed_mime_types={"image/png", "application/octet-stream"},
                max_bytes=100,
            ),
        )


def test_media_from_base64_checks_encoded_length_before_decoding():
    with pytest.raises(MediaError, match="size limit"):
        ImageObject.from_base64("AAAAAA==", max_encoded_length=4)


def test_media_download_rejects_redirects(monkeypatch):
    class Response:
        status_code = 302
        headers = {"location": "https://other.example/image.png"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class Client:
        def __init__(self, **kwargs):
            assert kwargs["follow_redirects"] is False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def stream(self, method, url):
            return Response()

    monkeypatch.setattr("httpx.Client", Client)
    with pytest.raises(MediaSecurityError, match="redirects are disabled"):
        download_media("https://example.com/image.png")


@pytest.mark.parametrize(
    "address",
    [
        "10.0.0.1",
        "127.0.0.1",
        "169.254.1.1",
        "240.0.0.1",
        "fc00::1",
        "::1",
        "fe80::1",
        "2001:db8::1",
    ],
)
def test_media_policy_rejects_non_public_dns_results(monkeypatch, address):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type: [
            (
                socket.AF_INET6 if ":" in address else socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (address, port),
            )
        ],
    )

    with pytest.raises(MediaSecurityError, match="non-public IP"):
        MediaPolicy().validate_url("https://media.example/resource")


def test_media_policy_allows_private_dns_results_when_explicitly_enabled(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port))
        ],
    )

    MediaPolicy(allow_private=True).validate_url("https://localhost/resource")


def test_media_policy_rejects_host_with_any_non_public_dns_answer(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", port)),
        ],
    )

    with pytest.raises(MediaSecurityError, match="non-public IP"):
        MediaPolicy().validate_url("https://mixed.example/resource")


def test_media_download_connects_only_to_the_validated_dns_address(monkeypatch):
    import httpcore

    dns_calls = []
    connection_hosts = []
    requested_urls = []

    def resolve(host, port, type):
        dns_calls.append(host)
        address = "93.184.216.34" if len(dns_calls) == 1 else "127.0.0.1"
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (address, port),
            )
        ]

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    def connect_tcp(self, host, port, **kwargs):
        connection_hosts.append(host)
        return object()

    monkeypatch.setattr(httpcore.SyncBackend, "connect_tcp", connect_tcp)

    class Response:
        status_code = 200
        headers = {"content-type": "image/png"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def raise_for_status(self):
            return None

        def iter_bytes(self):
            yield b"\x89PNG\r\n\x1a\n"

    class Client:
        def __init__(self, **kwargs):
            self.backend = kwargs["transport"]._pool._network_backend

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def stream(self, method, url):
            requested_urls.append(url)
            self.backend.connect_tcp(
                host="media.example",
                port=443,
                timeout=1,
                local_address=None,
                socket_options=None,
            )
            return Response()

    monkeypatch.setattr("httpx.Client", Client)

    assert download_media("https://media.example/image.png") == b"\x89PNG\r\n\x1a\n"
    assert requested_urls == ["https://media.example/image.png"]
    assert connection_hosts == ["93.184.216.34"]
    assert dns_calls == ["media.example"]
