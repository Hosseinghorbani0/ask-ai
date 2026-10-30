from collections.abc import Iterable
from dataclasses import fields
from typing import Any

from .base import BaseProvider
from .capabilities import Capabilities
from .exceptions import ProviderError


class Router:
    """Route requests across providers using a deterministic policy."""

    def __init__(
        self,
        providers: Iterable[Any],
        policy: str = "most_reliable",
        profiles: dict[str, dict[str, float]] | None = None,
    ):
        if policy not in {"cheapest", "fastest", "most_reliable"}:
            raise ValueError("policy must be cheapest, fastest, or most_reliable")
        self.providers = list(providers)
        self.policy = policy
        self.profiles = profiles or {}

    def _provider_name(self, provider: Any) -> str:
        return provider.__class__.__name__

    def _ordered(self) -> list[Any]:
        metric = {
            "cheapest": "cost",
            "fastest": "latency_ms",
            "most_reliable": "reliability",
        }[self.policy]
        default = 0.0 if metric == "reliability" else float("inf")

        def score(provider: Any) -> float:
            profile = self.profiles.get(self._provider_name(provider), {})
            value = profile.get(metric, default)
            return -value if metric == "reliability" else value

        return sorted(self.providers, key=score)

    def capabilities(self) -> Capabilities:
        if not self.providers:
            return Capabilities()
        capabilities = [provider.capabilities() for provider in self.providers]
        return Capabilities(
            **{
                field.name: all(getattr(item, field.name) for item in capabilities)
                for field in fields(Capabilities)
            }
        )

    def _is_retryable(self, error: Exception) -> bool:
        return BaseProvider._is_retryable_error(object(), error)

    def ask(self, query: str, **kwargs: Any):
        errors = []
        for provider in self._ordered():
            try:
                return provider.ask(query, **kwargs)
            except Exception as error:
                if not self._is_retryable(error):
                    raise
                errors.append(f"{self._provider_name(provider)}: {error}")
        raise ProviderError(f"All routed providers failed: {errors}")

    async def ask_async(self, query: str, **kwargs: Any):
        errors = []
        for provider in self._ordered():
            try:
                return await provider.ask_async(query, **kwargs)
            except Exception as error:
                if not self._is_retryable(error):
                    raise
                errors.append(f"{self._provider_name(provider)}: {error}")
        raise ProviderError(f"All routed providers failed: {errors}")

    def ask_stream(self, query: str, **kwargs: Any):
        errors = []
        for provider in self._ordered():
            emitted = False
            try:
                for chunk in provider.ask_stream(query, **kwargs):
                    emitted = True
                    yield chunk
                return
            except Exception as error:
                if emitted or not self._is_retryable(error):
                    raise
                errors.append(f"{self._provider_name(provider)}: {error}")
        raise ProviderError(f"All routed providers failed: {errors}")

    async def ask_stream_async(self, query: str, **kwargs: Any):
        errors = []
        for provider in self._ordered():
            emitted = False
            try:
                async for chunk in provider.ask_stream_async(query, **kwargs):
                    emitted = True
                    yield chunk
                return
            except Exception as error:
                if emitted or not self._is_retryable(error):
                    raise
                errors.append(f"{self._provider_name(provider)}: {error}")
        raise ProviderError(f"All routed providers failed: {errors}")
