# Migrating to ask-ai v0.6.0

## Python version

Python 3.10 is now the minimum supported version.

## Google SDK

The Google provider now uses `google-genai` instead of `google-generativeai`.
The public `GoogleProvider` constructor and ask methods are unchanged. Install
the optional provider with:

```bash
pip install "askai-python[google]"
```

Google async requests and streaming now use the SDK's native async client and
incremental stream APIs. The provider owns its SDK client; call `close()` or
`await aclose()` when its connection resources should be released.

## Structured responses

Existing `response_model` and `validation_retries` calls remain available.
Supported Pydantic, dataclass, `TypedDict`, and JSON Schema models are normalized
to strict JSON Schema and sent using each provider's native request format where
available. OpenAI and Azure use Chat Completions `response_format`; Anthropic
uses `output_config.format`; Groq and OpenRouter use Chat Completions
`response_format`; Google uses `response_mime_type` and `response_schema`.

If a native-format request receives a clear unsupported-schema error (HTTP 400
or 422), the adapter retries once without the native schema. It does not use
this fallback for authentication, rate-limit, or server errors. Schemas that
cannot be represented in the strict provider format go directly through the
existing prompt-based path. Local response validation and configured
`validation_retries` continue to apply in either path. The raw provider result
remains available as `response.raw`, and the parsed result as `response.parsed`.

Provider/model schema support varies, and live API behavior has not been
verified; these integrations are covered by mocks only.
The Anthropic optional dependency now requires SDK version 1.0.0 or newer for
the `output_config.format` parameter.

## Retry behavior

Provider SDK retries are disabled to avoid stacking them with ask-ai retries.
As a result, the default `retry=0` makes one request and does not retry transient
failures. Pass `retry=N` to enable ask-ai retries for retryable errors.

## Usage metadata

Provider-reported usage is normalized onto responses and streaming usage events
when the provider returns it. Cost estimates remain absent when usage is
unavailable. The extraction paths are mock-tested and have not been verified
against live provider APIs.
