# Migration guide for v0.5.0

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
`Completed`, and `Error` events.

## Observability

Use `provider.use(Observability(...))` to attach optional metadata and event
callbacks. Existing responses remain compatible; metadata is available through
`response.metadata`.

## Capability registry

Providers now expose `capabilities()` as advisory metadata. It can be used to
choose a provider without changing existing request behavior.

## Smart Router

`Router` is an optional higher-level API. Existing provider instances and
fallback behavior remain unchanged.

## Secure media

Use `MediaPolicy` and `download_media` for constrained downloads. Existing
provider-generated media continues to work, but now uses HTTPS and size
validation.

## Conversation sessions

Use `provider.session()` for optional in-memory history. Normal `ask()` calls
remain stateless and unchanged.
