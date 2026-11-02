# Changelog

## 0.6.0 - Unreleased

### Breaking changes

- The minimum supported Python version is now 3.10.

### Changed

- Provider SDK automatic retries are disabled to avoid retry stacking. The default `retry=0` therefore makes one request; set `retry` explicitly to enable ask-ai retries for retryable failures.

### Added

- Normalize provider-reported token usage on responses and streaming `UsageUpdate` events; estimated cost remains unavailable when usage is missing.
- Migrate the Google provider to the `google-genai` SDK with native async requests and incremental async streaming.
- Native JSON Schema requests for structured responses across supported providers, with narrowly scoped prompt-only fallback and continued local validation.
- Warn on unknown option names with spelling suggestions; opt-in `strict_options=True` raises an error. `safe_mode` emits a deprecation warning because it has no defined behavior.

## 0.5.0 - 2026-10-30

### Added

- Validated structured responses for Pydantic, dataclasses, `TypedDict`, and JSON Schema.
- Automatic validation retries with separate raw and parsed response access.
- Typed sync and async streaming events: `TextDelta`, `Completed`, and `Error`; `ToolCall` and `UsageUpdate` are reserved for future provider adapters.
- Optional observability middleware with provider, model, latency, and retry metadata. Provider usage extraction and failure-reason reporting are not supported yet; bundled adapters do not provide usage for cost estimates.
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
