"""Optional, user-run integration smoke checks against configured provider APIs."""

import asyncio
import importlib
import io
import json
import os
import re
import time
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Callable, Mapping, Optional
from unittest.mock import patch

from ask_ai import (
    Anthropic,
    Google,
    Groq,
    OpenAI,
    OpenRouter,
    Router,
)
from ask_ai.exceptions import ProviderTimeoutError

PROVIDER_SPECS = (
    ("OpenAI", "OPENAI_API_KEY", OpenAI, "gpt-4o-mini"),
    ("Anthropic", "ANTHROPIC_API_KEY", Anthropic, "claude-3-5-haiku-latest"),
    ("Google", "GOOGLE_API_KEY", Google, "gemini-2.5-flash-lite"),
    ("Groq", "GROQ_API_KEY", Groq, "llama-3.1-8b-instant"),
    ("OpenRouter", "OPENROUTER_API_KEY", OpenRouter, "openai/gpt-4o-mini"),
)

PROVIDER_CHECKS = (
    "plain_ask",
    "sync_streaming",
    "async_ask",
    "async_streaming",
    "structured_output",
    "usage_extraction",
    "fallback",
    "session",
    "timeout",
)
SECRET_ENV_VARS = tuple(spec[1] for spec in PROVIDER_SPECS)


def _record(
    results: list[dict[str, str]],
    provider: str,
    check: str,
    status: str,
    detail: str = "",
) -> None:
    results.append(
        {"provider": provider, "check": check, "status": status, "detail": detail}
    )


def _safe_error(error: Exception, env: Mapping[str, str]) -> str:
    message = f"{type(error).__name__}: {error}"
    for env_name in SECRET_ENV_VARS:
        value = env.get(env_name)
        if value:
            message = message.replace(value, "[REDACTED]")
    return re.sub(r"\b(?:sk|key)-[A-Za-z0-9_-]{12,}\b", "[REDACTED]", message)


def _check(
    results: list[dict[str, str]],
    provider_name: str,
    check_name: str,
    operation: Callable[[], str],
    env: Mapping[str, str],
) -> None:
    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            detail = operation()
    except Exception as error:
        _record(
            results,
            provider_name,
            check_name,
            "FAIL",
            _safe_error(error, env),
        )
    else:
        _record(results, provider_name, check_name, "PASS", detail)


def _require_text(text: Optional[str], action: str) -> str:
    if not text or not text.strip():
        raise AssertionError(f"{action} returned empty text")
    return text


def _structured_tracking_module(provider: Any):
    module_name = provider.__class__.__module__
    if provider.__class__.__name__ in {"AzureProvider", "OpenRouterProvider"}:
        module_name = "ask_ai.providers.openai_provider"
    return importlib.import_module(module_name)


def _track_structured_mode(provider: Any, tracker: dict[str, str]) -> ExitStack:
    stack = ExitStack()
    module = _structured_tracking_module(provider)

    sync_original = getattr(module, "call_with_schema_fallback", None)
    if callable(sync_original):
        def tracked_sync(call, native_kwargs, fallback_kwargs):
            def observe(**kwargs):
                tracker["mode"] = (
                    "native" if kwargs == native_kwargs else "prompt_fallback"
                )
                return call(**kwargs)

            return sync_original(observe, native_kwargs, fallback_kwargs)

        stack.enter_context(
            patch.object(module, "call_with_schema_fallback", tracked_sync)
        )

    async_original = getattr(module, "call_with_schema_fallback_async", None)
    if callable(async_original):
        def tracked_async(call, native_kwargs, fallback_kwargs):
            async def observe(**kwargs):
                tracker["mode"] = (
                    "native" if kwargs == native_kwargs else "prompt_fallback"
                )
                return await call(**kwargs)

            return async_original(observe, native_kwargs, fallback_kwargs)

        stack.enter_context(
            patch.object(module, "call_with_schema_fallback_async", tracked_async)
        )

    return stack


def _run_provider_checks(
    provider_name: str,
    provider_class: type,
    api_key: str,
    model: str,
    env: Mapping[str, str],
    results: list[dict[str, str]],
) -> Any:
    try:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            provider = provider_class(api_key=api_key, model=model, timeout=20)
    except Exception as error:
        _record(results, provider_name, "setup", "FAIL", _safe_error(error, env))
        for check in PROVIDER_CHECKS:
            _record(results, provider_name, check, "SKIP", "provider setup failed")
        return None

    def plain_ask() -> str:
        response = provider.ask("Reply with one short word: ready.", max_tokens=8, retry=0)
        return f"text={_require_text(response.text, 'ask')[:40]!r}"

    _check(results, provider_name, "plain_ask", plain_ask, env)

    def sync_streaming() -> str:
        chunks = list(
            provider.ask_stream(
                "Reply with one short word: ready.", max_tokens=8, timeout=20
            )
        )
        text = _require_text("".join(chunks), "sync streaming")
        return f"chunks={len(chunks)}, text={text[:40]!r}"

    _check(results, provider_name, "sync_streaming", sync_streaming, env)

    def async_ask() -> str:
        async def run():
            return await provider.ask_async(
                "Reply with one short word: ready.", max_tokens=8, retry=0
            )

        response = asyncio.run(run())
        return f"text={_require_text(response.text, 'async ask')[:40]!r}"

    _check(results, provider_name, "async_ask", async_ask, env)

    def async_streaming() -> str:
        async def run():
            chunks = []
            started = time.perf_counter()
            first_chunk_ms = None
            async for chunk in provider.ask_stream_async(
                "Reply with one short word: ready.", max_tokens=8, timeout=20
            ):
                if first_chunk_ms is None:
                    first_chunk_ms = (time.perf_counter() - started) * 1000
                chunks.append(chunk)
            return chunks, first_chunk_ms

        chunks, first_chunk_ms = asyncio.run(run())
        _require_text("".join(chunks), "async streaming")
        return f"chunks={len(chunks)}, first_chunk_ms={first_chunk_ms:.1f}"

    _check(results, provider_name, "async_streaming", async_streaming, env)

    def structured_output() -> str:
        from pydantic import BaseModel

        class SmokeResponse(BaseModel):
            answer: str
            note: Optional[str] = None
            label: str = "smoke"

        tracker: dict[str, str] = {}
        with _track_structured_mode(provider, tracker):
            response = provider.ask(
                "Return answer='ready', note=null, label='smoke'.",
                response_model=SmokeResponse,
                validation_retries=1,
                max_tokens=80,
                retry=0,
            )
        parsed = response.parsed
        if parsed.answer != "ready":
            raise AssertionError(f"unexpected structured answer: {parsed.answer!r}")
        return f"mode={tracker.get('mode', 'prompt_fallback')}, parsed={parsed!r}"

    _check(results, provider_name, "structured_output", structured_output, env)

    def usage_extraction() -> str:
        response = provider.ask(
            "Reply with one short word: ready.", max_tokens=8, retry=0
        )
        usage = response.metadata.usage
        if usage is None or any(
            value is None
            for value in (
                usage.input_tokens,
                usage.output_tokens,
                usage.total_tokens,
            )
        ):
            raise AssertionError("response.metadata.usage is missing token counts")
        if response.metadata.estimated_cost is not None:
            raise AssertionError("cost should be absent without pricing configuration")
        return (
            f"input={usage.input_tokens}, output={usage.output_tokens}, "
            f"total={usage.total_tokens}, estimated_cost=None"
        )

    _check(results, provider_name, "usage_extraction", usage_extraction, env)

    def fallback() -> str:
        invalid_provider = provider_class(
            api_key="invalid-smoke-test-key",
            model=model,
            timeout=20,
        )
        response = provider.ask(
            "Reply with one short word: ready.",
            providers=[invalid_provider, provider],
            max_tokens=8,
            retry=0,
        )
        return f"fallback text={_require_text(response.text, 'fallback')[:40]!r}"

    _check(results, provider_name, "fallback", fallback, env)

    def session() -> str:
        conversation = provider.session(max_messages=4)
        conversation.ask(
            "Remember the code word is kiwi. Reply only ready.",
            max_tokens=8,
            retry=0,
        )
        response = conversation.ask(
            "What is the code word? Reply with only the word.",
            max_tokens=8,
            retry=0,
        )
        text = _require_text(response.text, "session")
        if "kiwi" not in text.casefold():
            raise AssertionError(f"session did not retain the first turn: {text!r}")
        return f"second_turn={text[:40]!r}"

    _check(results, provider_name, "session", session, env)

    def timeout() -> str:
        long_prompt = "Summarize this text in one word: " + ("context " * 4000)
        try:
            provider.ask(long_prompt, timeout=1, max_tokens=4, retry=0)
        except ProviderTimeoutError as error:
            return f"mapped timeout: {type(error).__name__}"
        raise AssertionError("request did not raise ProviderTimeoutError")

    _check(results, provider_name, "timeout", timeout, env)
    return provider


def run_smoke(
    env: Optional[Mapping[str, str]] = None,
    report_path: Path | str = Path("smoke_report.json"),
) -> list[dict[str, str]]:
    """Run provider checks for keys present in env and save a secret-free report."""
    environment = os.environ if env is None else env
    results: list[dict[str, str]] = []
    available_providers = []

    for provider_name, env_name, provider_class, model in PROVIDER_SPECS:
        api_key = environment.get(env_name)
        if not api_key:
            for check in PROVIDER_CHECKS:
                _record(results, provider_name, check, "SKIP", f"{env_name} is not set")
            continue
        provider = _run_provider_checks(
            provider_name,
            provider_class,
            api_key,
            model,
            environment,
            results,
        )
        if provider is not None:
            available_providers.append(provider)

    if len(available_providers) < 2:
        _record(
            results,
            "Router",
            "two_provider_routing",
            "SKIP",
            "requires at least two providers with configured keys",
        )
    else:
        def route_with_two_providers() -> str:
            providers = available_providers[:2]
            profiles = {
                provider.__class__.__name__: {"reliability": 1.0}
                for provider in providers
            }
            router = Router(providers, policy="most_reliable", profiles=profiles)
            response = router.ask(
                "Reply with one short word: ready.",
                max_tokens=8,
                retry=0,
            )
            return f"text={_require_text(response.text, 'router')[:40]!r}"

        _check(
            results,
            "Router",
            "two_provider_routing",
            route_with_two_providers,
            environment,
        )

    report = {
        "results": results,
        "summary": {
            status: sum(result["status"] == status for result in results)
            for status in ("PASS", "FAIL", "SKIP")
        },
    }
    Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return results


def main() -> None:
    results = run_smoke()
    print(f"{'Provider':<12} {'Check':<22} {'Status':<6} Details")
    for result in results:
        print(
            f"{result['provider']:<12} {result['check']:<22} "
            f"{result['status']:<6} {result['detail']}"
        )
    print(f"JSON report written to {Path('smoke_report.json').resolve()}")


if __name__ == "__main__":
    main()
