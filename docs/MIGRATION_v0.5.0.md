# Migration guide for v0.5.0

The v0.5.0 APIs are additive. Existing `ask()`, `ask_stream()`, provider
classes, and response text access remain compatible.

## Structured responses

Existing `response_model=Model` calls remain supported. Use `response.parsed`
for validated Pydantic, dataclass, `TypedDict`, or JSON Schema output.
`response.raw` returns the unmodified provider text.

Set `validation_retries` to retry only when the model returns invalid structured
data. The default is `0`, so existing request behavior is preserved.

Install optional validation dependencies when needed:

```bash
pip install "askai-python[structured]"
```

## Streaming events

`ask_stream()` and `ask_stream_async()` still yield strings. New code can use
`ask_stream_events()` or `ask_stream_events_async()` for typed `TextDelta`,
`Completed`, and `Error` events. `ToolCall` and `UsageUpdate` are reserved event
types and are not emitted by the current adapters.

## Observability

Use `provider.use(Observability(...))` to attach optional metadata and event
callbacks. Existing responses remain compatible; metadata is available through
`response.metadata`.

## Capability registry

Providers now expose `capabilities()` as advisory metadata. It can be used to
choose a provider without changing existing request behavior; it is not an
enforcement layer.

## Smart Router

`Router` is an optional higher-level API. Existing provider instances and
fallback behavior remain unchanged. Its policies use static `profiles`; provide
latency, cost, or reliability values for meaningful ordering.

## Secure media

Use `MediaPolicy` and `download_media` for constrained downloads. Existing
provider-generated media continues to work, but now uses HTTPS, size, and
content-based MIME validation. Redirects are rejected rather than followed.

## Conversation sessions

Use `provider.session()` for optional in-memory history. Normal `ask()` calls
remain stateless and unchanged.
