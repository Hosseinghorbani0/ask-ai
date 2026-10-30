import pytest

from ask_ai import MediaPolicy, download_media
from ask_ai.exceptions import MediaSecurityError


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
