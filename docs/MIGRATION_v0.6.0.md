# Migrating to ask-ai v0.6.0

## Breaking changes

- Python 3.10 is now the minimum supported version.
- The optional Anthropic SDK dependency requires `anthropic>=1.0.0`.
- The Google provider dependency changed from `google-generativeai` to
  `google-genai`.
- Provider SDK-level retries are disabled; ask-ai applies its own retry policy.

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
`ConversationSession` supports validated `response_model` output for
non-streaming `ask()` and `ask_async()` calls. Streaming session methods reject
`response_model` because streamed output is not validated before it is yielded.
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
The default is `retry=2`, allowing up to three total attempts for retryable
timeouts/network errors, 429 rate limits, and 5xx provider errors. Retries use
exponential backoff with jitter; authentication and invalid-request errors are
not retried. Pass `retry=0` to make one attempt, or `retry=N` to choose another
retry count. Streaming requests retry only before the first chunk/event; after
output begins, errors propagate without restarting the stream. Connection
failures are reported as `ProviderConnectionError`, distinct from
`ProviderTimeoutError`.

## Option validation and `safe_mode`

Unknown option names now produce a `UserWarning` with a spelling suggestion.
Set `strict_options=True` on a provider, session, or request to raise a
`ValueError` instead. `safe_mode` has no defined behavior and emits a
`DeprecationWarning` when supplied; it should not be relied on.

## Usage metadata

Provider-reported usage is normalized onto responses and streaming usage events
when the provider returns it. Cost estimates remain absent when usage is
unavailable. The extraction paths are mock-tested and have not been verified
against live provider APIs. On request failures, observability middleware emits
a `failed` event containing `failure_reason`; the exception still propagates.
