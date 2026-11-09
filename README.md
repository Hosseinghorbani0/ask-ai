# ask-ai

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![Python versions](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A small, typed Python SDK for calling several LLM providers through a consistent API.**
Use it from scripts and Python applications without adopting a larger orchestration framework.

`ask-ai` is a client library, not a hosted service or gateway. You create a provider client, call it synchronously or asynchronously, and receive a common `Response` object. Provider SDKs are optional; install only the ones you use.

## Documentation languages

[English](README.md) · [العربية](docs/README_ar.md) · [فارسی](docs/README_fa.md) · [Español](docs/README_es.md) · [日本語](docs/README_ja.md) · [Русский](docs/README_ru.md) · [Türkçe](docs/README_tr.md) · [中文](docs/README_zh.md)

## Contents

- [Features](#features)
- [Requirements and installation](#requirements-and-installation)
- [Providers](#providers)
- [Quick start](#quick-start)
- [Public API](#public-api)
- [Request options](#request-options)
- [Retries, fallback, and routing](#retries-fallback-and-routing)
- [Structured output](#structured-output)
- [Streaming and asynchronous use](#streaming-and-asynchronous-use)
- [Media generation and secure downloads](#media-generation-and-secure-downloads)
- [Conversation sessions and client lifecycle](#conversation-sessions-and-client-lifecycle)
- [Capabilities and observability](#capabilities-and-observability)
- [Architecture](#architecture)
- [CLI](#command-line-interface)
- [Compatibility and troubleshooting](#compatibility-and-troubleshooting)
- [Contributing, support, and license](#contributing-support-and-license)

## Features

- Consistent `ask`, `ask_async`, `ask_stream`, and `ask_stream_async` APIs.
- Optional provider fallback and policy-based routing.
- Retry handling for transient failures, with per-call and total deadlines.
- Typed response metadata, normalized token usage, and optional observability hooks.
- JSON and validated structured responses for supported providers.
- Optional in-memory conversation sessions.
- OpenAI-compatible Chat Completions endpoints, including local servers.
- Secure, policy-controlled media downloads.

The public request API currently sends text; provider capability metadata does not imply vision input support. Tool-call execution and persistent conversation storage are not provided.

## Requirements and installation

- Python 3.10+ is required.
- Core package dependencies are empty. Provider SDKs and media/structured-output libraries are optional extras.

Install the base package:

```bash
python -m pip install askai-python
```

Install only the provider SDKs you need:

```bash
python -m pip install "askai-python[openai,groq]"   # OpenAI and Groq
python -m pip install "askai-python[openai]"       # OpenAI, Azure OpenAI, OpenRouter, compatible endpoints
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic and jsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # secure media downloads
python -m pip install "askai-python[all]"
```

Set credentials in your environment or pass `api_key=` when constructing a provider. Avoid hard-coding secrets in source code.

## Providers

| Provider | Import | Extra | Credential environment variable | Default model |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | Deployment name required |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| OpenAI-compatible | `OpenAICompatibleProvider` | `openai` | None (optional) | Required at construction |

Azure also requires `AZURE_OPENAI_ENDPOINT`; its deployment can be provided as `model=` or through `AZURE_OPENAI_DEPLOYMENT_NAME`. `AZURE_OPENAI_API_VERSION` defaults to `2024-06-01`. The compatible provider requires an absolute HTTP(S) `base_url` and a model; `api_key` may be omitted for local endpoints.

`capabilities()` returns declared support for text, streaming, async streaming, structured output, tool calls, image generation, audio generation, and vision. These are provider declarations, not a guarantee that every model or account enables the feature. In particular, tool-call execution and vision input are not exposed as general request features.

## Quick start

```python
from ask_ai import OpenAI

client = OpenAI()  # Reads OPENAI_API_KEY
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

Switch providers by using a different provider class:

```python
from ask_ai import Anthropic, Google, Groq

answer = Groq().ask("Give me one useful shell tip.")
print(answer.text)
```

## Public API

| Method | Result | Description |
|---|---|---|
| `provider.ask(query, **options)` | `Response` | Synchronous request |
| `await provider.ask_async(query, **options)` | `Response` | Native asynchronous request |
| `provider.ask_stream(query, **options)` | Iterator of strings | Synchronous text stream |
| `async for chunk in provider.ask_stream_async(query, **options)` | Async iterator of strings | Asynchronous text stream |
| `provider.ask_stream_events(query, **options)` | Iterator of event objects | Typed synchronous stream |
| `provider.ask_stream_events_async(query, **options)` | Async iterator of event objects | Typed asynchronous stream |

The `Response` provides `text`, unmodified `raw`, parsed `json`, `parsed`/`pydantic` when `response_model` was requested, optional `media`, `usage`, and `metadata`. `response.json` parses the response text; use `json=True` to request JSON-style output, or `response_model=...` when validation is required.

## Request options

Pass options to a request or set defaults using `provider.advanced(...)`. Options are merged, with request options taking precedence.

| Option | Purpose |
|---|---|
| `temperature`, `max_tokens`, `top_p` | Common generation controls |
| `frequency_penalty`, `presence_penalty`, `stop` | Provider-supported sampling controls |
| `system_message` (aliases: `system`, `prompt`) | System instruction |
| `timeout` | Timeout for an individual provider call (default 30 seconds in provider clients) |
| `total_timeout` | Deadline for the complete operation, including retries |
| `retry` | Additional retry count; defaults to 2 (up to 3 attempts) |
| `json=True` | Request JSON-formatted output and allow parsing via `response.json` |
| `response_model`, `validation_retries` | Parse and validate a supported structured model |
| `output_type` | Request supported generated `image` or `audio` output |
| `clean`, `strip`, `code` | Apply text cleanup/extraction when reading `response.text` |
| `strict_options=True` | Raise on unknown options instead of warning |

Provider/model support for individual options varies. Unknown options warn by default; strict mode raises `ValueError`. The deprecated `safe_mode` option has no defined behavior. Unsupported output types raise rather than being silently ignored.

```python
response = client.ask(
    "Summarize this topic in three bullets.",
    temperature=0.2,
    max_tokens=250,
    system_message="Be concise and factual.",
    total_timeout=20,
)
```

## Retries, fallback, and routing

Requests default to two retries for retryable transient failures (up to three attempts). Invalid requests, authentication failures, and other non-retryable errors are not retried. `Retry-After` is honored within a 30-second clamp. `timeout` limits an individual call; `total_timeout` bounds the complete retry operation.

Fallback can try provider classes or instances:

```python
from ask_ai import OpenAI, Groq

response = OpenAI().ask("Hello", providers=[OpenAI, Groq], retry=1)
```

The fallback chain advances only for retryable provider failures. `Router` provides policy-based selection and an overall `max_attempts` budget:

```python
from ask_ai import OpenAI, Groq, Router

router = Router([OpenAI(), Groq()], max_attempts=2)
response = router.ask("Hello", retry=1)
```

Retries and fallbacks can multiply requests and associated provider charges. Set a small retry count and a total deadline for cost- and latency-sensitive work. A stream is not retried after chunks have already been yielded.

## Structured output

Use `response_model` with supported Pydantic models, dataclasses, `TypedDict`, or JSON Schema definitions. The request returns a regular `Response`; access the validated result through `.parsed`:

```python
from pydantic import BaseModel
from ask_ai import OpenAI

class Summary(BaseModel):
    title: str
    points: list[str]

response = OpenAI().ask(
    "Summarize the water cycle.",
    response_model=Summary,
    validation_retries=1,
)
summary = response.parsed
print(summary.title)
```

Provider-side structured-output support differs. Validation is performed locally, and unsupported or invalid output raises a structured validation error rather than guaranteeing a provider-specific strict schema mode. Structured validation is not supported by session streaming methods.

## Streaming and asynchronous use

```python
for chunk in client.ask_stream("Write a short greeting."):
    print(chunk, end="", flush=True)
```

Async methods use provider async clients:

```python
import asyncio
from ask_ai import OpenAI

async def main():
    client = OpenAI()
    response = await client.ask_async("Give me a concise definition of an API.")
    print(response.text)
    async for chunk in client.ask_stream_async("Now say it in five words."):
        print(chunk, end="", flush=True)
    await client.aclose()

asyncio.run(main())
```

Typed stream events include `TextDelta`, `UsageUpdate`, `Completed`, and `Error`. `ToolCall` is exported as an event type, but current provider adapters do not emit tool-call events. Use `ask_stream_events` or `ask_stream_events_async` when event objects are preferable to text chunks. Catch cancellation and provider exceptions in the calling application as appropriate.

## Media generation and secure downloads

Some provider implementations support generated image or audio output through `output_type="image"` or `output_type="audio"`. Availability depends on provider and model; inspect `capabilities()` and provider documentation. The request API does not currently accept image input for vision.

Secure media downloads require the optional `httpx` extra. By default, downloads require HTTPS, reject redirects and non-public DNS results, and enforce a 25 MiB limit and 30-second timeout. You may restrict MIME types and hosts:

```python
from ask_ai import MediaPolicy, download_media

data = download_media(
    "https://example.com/image.png",
    MediaPolicy(
        max_bytes=10 * 1024 * 1024,
        allowed_mime_types={"image/png"},
        allowed_hosts={"example.com"},
    ),
)
```

Only set `allow_private=True` for trusted private-network URLs. A media policy does not make arbitrary provider-generated URLs safe to use elsewhere.

## Conversation sessions and client lifecycle

`provider.session()` creates an optional in-memory conversation:

```python
with OpenAI() as client:
    session = client.session(max_messages=20)
    session.ask("My name is Ada.")
    print(session.ask("What is my name?").text)
```

History is held in process memory and is not persisted. `max_messages` bounds retained messages by user/assistant pairs. Concurrent sync operations serialize separately from async operations; do not mix sync and async operations concurrently on one session.

Providers support `close()`/`aclose()` and synchronous/asynchronous context managers. Close clients when finished, especially in long-running services. A cached async client is bound to the first event loop that uses it; use a provider instance per loop.

## Capabilities and observability

Use `provider.capabilities()` to inspect declared provider support. Attach an observability hook with `provider.use(Observability(...))` to receive request metadata such as provider, model, latency, retry count, and normalized token usage. Estimated cost is available only when pricing rates are supplied and usage is reported by the provider.

```python
from ask_ai import Observability, OpenAI

events = []
client = OpenAI()
client.use(Observability(on_event=events.append))
response = client.ask("Return one word.")
print(response.metadata)
```

Avoid putting prompts, personal data, or credentials into your own telemetry handlers. Hook exceptions are isolated from the request path.

## Architecture

`ask_ai` provides a shared provider base, provider-specific SDK adapters, a common `Response`, optional `Router` and `ConversationSession`, and utilities for structured output and media security. Provider SDKs are imported optionally, so importing the package does not require installing every integration. The library does not proxy requests through its own service.

## Command-line interface

The `ask-ai` command is installed with the package. It supports OpenAI, Groq, Google, OpenRouter, Azure, and Anthropic:

```bash
ask-ai --provider openai "Explain recursion in one sentence."
ask-ai --provider groq --stream "List three Python tips."
ask-ai --help
```

The CLI uses the selected provider's environment credentials. The generic OpenAI-compatible provider is available through the Python API, not the current CLI provider choices.

## Compatibility and troubleshooting

- **Python:** 3.10–3.13 are listed in package classifiers; the declared minimum is 3.10.
- **Typing:** the distribution includes `ask_ai/py.typed`.
- **Operating systems:** the package is pure Python; provider SDK support and network behavior depend on your platform and installed SDK.
- **No SDK installed:** install the matching provider extra, for example `askai-python[openai]`.
- **Missing credentials:** set the provider environment variable listed above, or pass `api_key=`.
- **Azure initialization fails:** set `AZURE_OPENAI_ENDPOINT`, API key, and a deployment name/model.
- **Unknown option warning:** check the spelling, or set `strict_options=True` to fail immediately.
- **Async loop error:** do not reuse an async provider client across event loops; construct one provider per loop.
- **Structured output invalid:** validate the model/schema and increase `validation_retries` only when another billed attempt is acceptable.
- **Live provider behavior:** mock-based tests do not guarantee that a live provider accepts a model or option. Real-provider checks are optional and may incur charges.

## Contributing, support, and license

Bug reports and feature requests are welcome via the [issue tracker](https://github.com/Hosseinghorbani0/ask-ai/issues). For code contributions, open a focused pull request with tests and documentation updates for behavior changes. Run the project checks locally:

```bash
python -m pytest -q
ruff check .
```

Review [CHANGELOG.md](CHANGELOG.md) for release history. Usage questions and bug reports should include a minimal reproducible example and omit API keys, personal data, and other secrets.

Licensed under the [MIT License](LICENSE). See the [PyPI project page](https://pypi.org/project/askai-python/) and [GitHub repository](https://github.com/Hosseinghorbani0/ask-ai) for releases and project updates.
