# Changelog

## 0.6.0 - Unreleased

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
