# Changelog

## 0.5.0 - 2026-10-30

### Added

- Validated structured responses for Pydantic, dataclasses, `TypedDict`, and JSON Schema.
- Automatic validation retries with separate raw and parsed response access.
- Typed sync and async streaming events: `TextDelta`, `ToolCall`, `UsageUpdate`, `Completed`, and `Error`.
- Optional observability middleware with latency, retry, usage, and estimated cost metadata.
- Provider capability registry through `capabilities()`.
- Policy-based Smart Router for cheapest, fastest, and most reliable routing.
- Secure media downloads with HTTPS, host, MIME, size, and timeout policies.
- Optional in-memory conversation sessions with sync, async, and streaming APIs.

### Compatibility

- Existing provider and legacy text streaming APIs remain available.
- New features are opt-in and do not require changes to existing `ask()` calls.

See [the v0.5.0 migration guide](docs/MIGRATION_v0.5.0.md) for details.
