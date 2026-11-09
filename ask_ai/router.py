import math
import time
from collections.abc import Iterable
from dataclasses import fields
from typing import Any, Optional

from .base import BaseProvider
from .capabilities import Capabilities
from .exceptions import ProviderError, ProviderTimeoutError, safe_provider_error_label


class Router:
    """Route requests across providers using a deterministic policy."""

    def __init__(
        self,
        providers: Iterable[Any],
        policy: str = "most_reliable",
        profiles: Optional[dict[str, dict[str, float]]] = None,
        max_attempts: Optional[int] = None,
    ):
        if policy not in {"cheapest", "fastest", "most_reliable"}:
            raise ValueError("policy must be cheapest, fastest, or most_reliable")
        self.providers = list(providers)
        self.policy = policy
        self.profiles = profiles or {}
        if max_attempts is not None and (
            isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or max_attempts < 1
        ):
            raise ValueError("max_attempts must be a positive integer.")
        self.max_attempts = max_attempts if max_attempts is not None else len(self.providers)

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

    def _request_plan(self, kwargs: dict[str, Any]):
        call_kwargs = dict(kwargs)
        total_timeout = call_kwargs.get("total_timeout")
        if total_timeout is None:
            deadline = None
        else:
            total_timeout = float(total_timeout)
            if not math.isfinite(total_timeout) or total_timeout <= 0:
                raise ValueError("total_timeout must be a finite positive number.")
            deadline = time.monotonic() + total_timeout
        call_kwargs["retry"] = 0
        return self._ordered()[: self.max_attempts], call_kwargs, deadline

    @staticmethod
    def _kwargs_for_attempt(kwargs: dict[str, Any], deadline: Optional[float]) -> dict[str, Any]:
        if deadline is None:
            return kwargs
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ProviderTimeoutError("Total router request deadline exceeded.")
        return {**kwargs, "total_timeout": remaining}

    def ask(self, query: str, **kwargs: Any):
        errors = []
        last_error = None
        providers, call_kwargs, deadline = self._request_plan(kwargs)
        for provider in providers:
            try:
                response = provider.ask(
                    query,
                    **self._kwargs_for_attempt(call_kwargs, deadline),
                )
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.")
                return response
            except Exception as error:
                if not self._is_retryable(error):
                    raise
                last_error = error
                errors.append(safe_provider_error_label(self._provider_name(provider), error))
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.") from error
        raise ProviderError(f"All routed providers failed: {errors}") from last_error

    async def ask_async(self, query: str, **kwargs: Any):
        errors = []
        last_error = None
        providers, call_kwargs, deadline = self._request_plan(kwargs)
        for provider in providers:
            try:
                response = await provider.ask_async(
                    query,
                    **self._kwargs_for_attempt(call_kwargs, deadline),
                )
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.")
                return response
            except Exception as error:
                if not self._is_retryable(error):
                    raise
                last_error = error
                errors.append(safe_provider_error_label(self._provider_name(provider), error))
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.") from error
        raise ProviderError(f"All routed providers failed: {errors}") from last_error

    def ask_stream(self, query: str, **kwargs: Any):
        errors = []
        last_error = None
        providers, call_kwargs, deadline = self._request_plan(kwargs)
        for provider in providers:
            emitted = False
            try:
                for chunk in provider.ask_stream(
                    query,
                    **self._kwargs_for_attempt(call_kwargs, deadline),
                ):
                    if deadline is not None and time.monotonic() >= deadline:
                        raise ProviderTimeoutError("Total router request deadline exceeded.")
                    emitted = True
                    yield chunk
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.")
                return
            except Exception as error:
                if emitted or not self._is_retryable(error):
                    raise
                last_error = error
                errors.append(safe_provider_error_label(self._provider_name(provider), error))
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.") from error
        raise ProviderError(f"All routed providers failed: {errors}") from last_error

    async def ask_stream_async(self, query: str, **kwargs: Any):
        errors = []
        last_error = None
        providers, call_kwargs, deadline = self._request_plan(kwargs)
        for provider in providers:
            emitted = False
            try:
                async for chunk in provider.ask_stream_async(
                    query,
                    **self._kwargs_for_attempt(call_kwargs, deadline),
                ):
                    if deadline is not None and time.monotonic() >= deadline:
                        raise ProviderTimeoutError("Total router request deadline exceeded.")
                    emitted = True
                    yield chunk
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.")
                return
            except Exception as error:
                if emitted or not self._is_retryable(error):
                    raise
                last_error = error
                errors.append(safe_provider_error_label(self._provider_name(provider), error))
                if deadline is not None and time.monotonic() >= deadline:
                    raise ProviderTimeoutError("Total router request deadline exceeded.") from error
        raise ProviderError(f"All routed providers failed: {errors}") from last_error
