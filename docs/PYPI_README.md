# ask-ai

[![PyPI version](https://img.shields.io/pypi/v/askai-python.svg)](https://pypi.org/project/askai-python/)
[![Python versions](https://img.shields.io/pypi/pyversions/askai-python.svg)](https://pypi.org/project/askai-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A small, typed Python SDK for calling several LLM providers through a consistent API.**
Use it from scripts and Python applications without adopting a larger orchestration framework.

`ask-ai` is a client library, not a hosted service or gateway. Create a provider client, call it synchronously or asynchronously, and receive a common `Response` object. Provider SDKs are optional; install only the ones you use.

- [Full documentation and language versions](https://github.com/Hosseinghorbani0/ask-ai#readme)
- [Report an issue](https://github.com/Hosseinghorbani0/ask-ai/issues)

## Features

- Sync, async, and streaming text request APIs.
- Provider fallback and policy-based routing.
- Retries for transient failures, individual-call timeouts, and total deadlines.
- JSON and validated structured responses for supported providers.
- Typed response metadata, normalized token usage, and optional observability hooks.
- Optional in-memory conversation sessions.
- OpenAI-compatible Chat Completions endpoints, including local servers.
- Policy-controlled secure media downloads.

The public request API currently sends text; vision input and persistent session storage are not provided. Tool-call execution is not provided.

## Requirements and installation

Python 3.10 or newer is required. Core dependencies are empty; provider SDKs are optional extras.

```bash
python -m pip install askai-python
python -m pip install "askai-python[openai]"       # OpenAI, Azure OpenAI, OpenRouter, compatible endpoints
python -m pip install "askai-python[anthropic]"
python -m pip install "askai-python[google]"
python -m pip install "askai-python[groq]"
python -m pip install "askai-python[structured]"   # Pydantic and jsonschema
python -m pip install "askai-python[media]"        # Pillow
python -m pip install "askai-python[httpx]"        # secure media downloads
python -m pip install "askai-python[all]"
```

Set the provider credential in an environment variable or pass `api_key=` to its constructor. Never commit credentials to source control.

## Providers

| Provider | Import | Extra | Environment variable | Default model |
|---|---|---|---|---|
| OpenAI | `OpenAI` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Anthropic | `Anthropic` | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| Groq | `Groq` | `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` |
| Azure OpenAI | `Azure` | `openai` | `AZURE_OPENAI_API_KEY` | Deployment required |
| OpenRouter | `OpenRouter` | `openai` | `OPENROUTER_API_KEY` | `openai/gpt-4o` |
| OpenAI-compatible | `OpenAICompatibleProvider` | `openai` | None (optional) | Required |

Azure also needs `AZURE_OPENAI_ENDPOINT`. Its deployment can be supplied as `model=` or through `AZURE_OPENAI_DEPLOYMENT_NAME`; `AZURE_OPENAI_API_VERSION` defaults to `2024-06-01`. The compatible provider requires an absolute HTTP(S) `base_url` and a model; `api_key` is optional for local servers.

`capabilities()` describes declared provider/model features. It does not guarantee availability for a particular model or account. In particular, vision input and tool-call execution are not general request features.

## Quick start and API

```python
from ask_ai import OpenAI

client = OpenAI()  # Reads OPENAI_API_KEY
response = client.ask("Explain what a Python context manager does.")
print(response.text)
```

The public methods are `ask()` (sync), `ask_async()` (async), `ask_stream()` (sync text iterator), `ask_stream_async()` (async text iterator), and their typed event variants `ask_stream_events()` and `ask_stream_events_async()`.

`Response` exposes `text`, unmodified `raw`, parsed `json`, `parsed`/`pydantic` for validated structured results, optional `media`, `usage`, and `metadata`.

## Request options and reliability

Set options per request or via `provider.advanced(...)`. Common options include `temperature`, `max_tokens`, `top_p`, `frequency_penalty`, `presence_penalty`, `stop`, `system_message` (also `system` or `prompt`), `timeout`, `total_timeout`, `retry`, `json`, `response_model`, `validation_retries`, `output_type`, `clean`, `strip`, `code`, and `strict_options`.

Unknown options warn by default; `strict_options=True` raises `ValueError`. Provider support for individual options varies. `timeout` limits an individual provider call; `total_timeout` bounds the complete operation. Retry defaults to 2 additional attempts for transient failures, honors `Retry-After` with a 30-second clamp, and does not retry non-retryable errors. Retry/fallback requests can incur additional charges. A stream is not retried after chunks have been yielded.

Fallback can be requested with `providers=[OpenAI, Groq]`. `Router` provides policy-based selection and a `max_attempts` budget. See the [full guide](https://github.com/Hosseinghorbani0/ask-ai#retries-fallback-and-routing) for examples.

## Structured output

Supported schemas include Pydantic models, dataclasses, `TypedDict`, and JSON Schema. Validation happens locally; access the result through `response.parsed`. Provider-native strict schema behavior differs. Structured validation is not available on session streaming methods.

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
print(response.parsed.title)
```

## Async, media, sessions, and lifecycle

```python
import asyncio
from ask_ai import OpenAI

async def main():
    async with OpenAI() as client:
        response = await client.ask_async("Define an API.")
        print(response.text)
        async for chunk in client.ask_stream_async("Say it in five words."):
            print(chunk, end="", flush=True)

asyncio.run(main())
```

Some providers implement generated image/audio responses using `output_type="image"` or `"audio"`; availability varies by provider and model. Image input for vision is not currently exposed by the request API. Secure media downloads require the `httpx` extra; downloads require HTTPS, reject redirects and non-public DNS answers by default, and enforce a 25 MiB limit and 30-second timeout. `MediaPolicy` can further restrict allowed hosts and MIME types.

`provider.session()` provides optional in-memory conversation history; it is not persisted. Providers support `close()`/`aclose()` and sync/async context managers. An async client belongs to the event loop that first uses it; create one provider per loop.

## Observability and troubleshooting

`provider.use(Observability(on_event=...))` receives request metadata, latency, retries, and reported token usage. Estimated cost requires supplied pricing rates and provider usage. Do not send secrets or sensitive prompts to custom telemetry.

- Install the matching extra if a provider SDK is missing.
- Set the provider's environment key or pass `api_key=`.
- For Azure, configure the endpoint and deployment as well as credentials.
- Construct a fresh provider if an async event-loop ownership error occurs.
- Confirm model and option support with the provider; mock tests cannot guarantee live API behavior.
- Live integration calls may incur charges.

Python 3.10–3.13 are listed in package classifiers. The package includes `ask_ai/py.typed`.

## License and support

Distributed under the [MIT License](https://github.com/Hosseinghorbani0/ask-ai/blob/main/LICENSE). For bug reports and feature requests, use the [GitHub issue tracker](https://github.com/Hosseinghorbani0/ask-ai/issues). Please include a minimal reproducible example and remove API keys, personal information, and other secrets.
