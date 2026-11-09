# Changelog

## Unreleased

- Redact provider exception messages from fallback logs, aggregate errors, and failure observability events while preserving the original exception as the aggregate cause.
- Stop provider fallback on non-retryable request, authentication, and configuration errors across text and streaming APIs.
- Stream synchronous custom-provider chunks incrementally through the async adapter and close the source on early exit or cancellation.
- Add request-wide `total_timeout`, honor bounded provider `Retry-After` hints, and cap Router calls with `max_attempts` to prevent retry multiplication.
- Serialize sync and async operations independently per conversation session to keep concurrent request history coherent.
- Forward Anthropic stop sequences, align Google structured-output capabilities, and reject unsupported image inputs and output types explicitly.
- Align `Response.json` with JSON scalar/container values, validate `to_model()` through the structured parser, and accept empty JSON Schemas.
- Add provider sync/async close and context-manager APIs and reject reuse of cached async clients across event loops.
- Add `OpenAICompatibleProvider` for configured OpenAI Chat Completions-compatible endpoints with conservative capabilities.
- Add a parametrized provider contract suite for all built-in providers and `OpenAICompatibleProvider`, covering imports, normalized responses, error mapping/redaction, streaming lifecycle, option forwarding, structured output, capabilities, client cleanup, and event-loop ownership.
- Extend structured dataclass parsing for nested models, optional/union fields, enums, and provider contract coverage for Pydantic v1/v2 and bounded malformed/fenced JSON retries.
- Forward Google stop sequences through generation config.
- Expand CI to Windows and add a Python 3.13 coverage report, a focused mypy check for the OpenAI-compatible provider, and a clean-environment pip-audit job.
- Add table-driven media URL checks for embedded credentials, IDNA allowlists, IPv4-mapped and alternate numeric IP forms, changing DNS answers, and invalid or mismatched Content-Length values; reject URL userinfo and malformed lengths.

### Fixed

- Add validated structured responses to non-streaming conversation sessions and preserve configured system prompts in session history.
- Isolate retry counters across concurrent request contexts, reject negative retry counts, redact response content from repr/JSON parse errors, and expose media category through `MediaObject.type`.

## 0.6.0 - 2026-11-02

### Breaking changes

- The minimum supported Python version is now 3.10.
- The Anthropic optional SDK dependency now requires version 1.0.0 or newer.
- The Google provider now uses `google-genai` instead of `google-generativeai`.
- Provider SDK-level automatic retries are disabled; ask-ai owns retry behavior.

### Changed

- Ask-ai retries transient timeout/network, 429, and 5xx failures by default (`retry=2`, up to three total attempts); non-retryable errors are not retried. Set `retry=0` to disable retries.

### Added

- Normalize provider-reported token usage on responses and streaming `UsageUpdate` events; estimated cost remains unavailable when usage is missing.
- Migrate the Google provider to the `google-genai` SDK with native async requests and incremental async streaming.
- Native JSON Schema requests for structured responses across supported providers, with narrowly scoped prompt-only fallback and continued local validation.
- Warn on unknown option names with spelling suggestions; opt-in `strict_options=True` raises an error. `safe_mode` emits a deprecation warning because it has no defined behavior.
- Emit observability failure events with `failure_reason`; usage extraction, structured output, and streaming usage events are mock-tested but have not been verified against live provider APIs.
- Retry transient streaming failures only before the first chunk/event; classify network connection failures separately from timeouts.

## 0.5.0 - 2026-10-30

### Added

- Validated structured responses for Pydantic, dataclasses, `TypedDict`, and JSON Schema.
- Automatic validation retries with separate raw and parsed response access.
- Typed sync and async streaming events: `TextDelta`, `Completed`, and `Error`; `ToolCall` and `UsageUpdate` are reserved for future provider adapters.
- Optional observability middleware with provider, model, latency, and retry metadata. In v0.5.0, provider usage extraction and failure-reason reporting were not supported yet; these were added in v0.6.0.
- Provider capability registry through `capabilities()`.
- Policy-based Smart Router for cheapest, fastest, and most reliable routing.
- Secure media downloads with HTTPS, host, MIME, size, and timeout policies.
- Optional in-memory conversation sessions with sync, async, and streaming APIs.

### Not supported yet

- Structured `response_model` validation in conversation sessions.

### Compatibility

- Existing provider and legacy text streaming APIs remain available.
- New features are opt-in and do not require changes to existing `ask()` calls.

See [the v0.5.0 migration guide](docs/MIGRATION_v0.5.0.md) for details.
