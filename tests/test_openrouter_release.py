import asyncio

from ask_ai.providers.openrouter_provider import OpenRouterProvider


class _Response:
    def raise_for_status(self):
        return None

    def json(self):
        return {"data": [{"url": "https://cdn.example/image.png"}]}


def _provider():
    provider = object.__new__(OpenRouterProvider)
    provider.api_key = "test-key"
    provider.model = "test-model"
    return provider


def test_openrouter_sync_image_uses_bearer_header(monkeypatch):
    captured = {}

    def post(url, **kwargs):
        captured.update(kwargs)
        return _Response()

    monkeypatch.setattr("httpx.post", post)
    monkeypatch.setattr(
        "ask_ai.providers.openai_provider._download_bytes",
        lambda url, timeout: b"\x89PNG\r\n\x1a\n",
    )

    _provider()._generate_image([{"content": "draw"}], type("Config", (), {"extra": {}})())

    assert captured["headers"]["Authorization"] == "Bearer test-key"


def test_openrouter_async_image_uses_bearer_header(monkeypatch):
    captured = {}

    class AsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, **kwargs):
            captured.update(kwargs)
            return _Response()

    monkeypatch.setattr("httpx.AsyncClient", AsyncClient)
    monkeypatch.setattr(
        "ask_ai.providers.openai_provider._download_bytes_async",
        lambda url, timeout: _completed_bytes(),
    )

    async def run():
        return await _provider()._generate_image_async(
            [{"content": "draw"}], type("Config", (), {"extra": {}})()
        )

    asyncio.run(run())

    assert captured["headers"]["Authorization"] == "Bearer test-key"


async def _completed_bytes():
    return b"\x89PNG\r\n\x1a\n"
