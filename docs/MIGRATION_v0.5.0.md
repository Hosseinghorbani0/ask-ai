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
