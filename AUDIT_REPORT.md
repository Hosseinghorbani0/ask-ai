# ask-ai Python SDK: library-maintainer audit

**Scope:** the checked-out Python library and its behavior as imported by downstream scripts, services, async applications, threaded programs, and serverless jobs. This audit is not an application deployment review.

**Status:** current dispositions are in Section 12; that table supersedes the initial-revision labels and proposed patches below. No provider credentials or live billable API calls were used.

## 1. Coverage and evidence

### File inventory

Every tracked text file below was read in full in the initial audit. The original inventory was updated for round-two changes and new files; unchanged-file counts remain from that full-read inventory. `AUDIT_REPORT.md`, generated `dist/`, caches, and ignored build artifacts are excluded from this self-referential inventory. `py.typed` is intentionally empty.

| File | Lines | Fully read |
|---|---:|:---:|
| `.flake8` | 11 | Yes |
| `.github/workflows/ci.yml` | 60 | Yes |
| `.github/workflows/publish.yml` | 100 | Yes |
| `.gitignore` | 35 | Yes |
| `CHANGELOG.md` | 50 | Yes |
| `LICENSE` | 21 | Yes |
| `README.md` | 334 | Yes |
| `ask_ai/__init__.py` | 79 | Yes |
| `ask_ai/__main__.py` | 4 | Yes |
| `ask_ai/base.py` | 1207 | Yes |
| `ask_ai/capabilities.py` | 17 | Yes |
| `ask_ai/cli.py` | 93 | Yes |
| `ask_ai/config.py` | 126 | Yes |
| `ask_ai/events.py` | 41 | Yes |
| `ask_ai/exceptions.py` | 95 | Yes |
| `ask_ai/media.py` | 481 | Yes |
| `ask_ai/media_security.py` | 177 | Yes |
| `ask_ai/observability.py` | 84 | Yes |
| `ask_ai/providers/__init__.py` | 16 | Yes |
| `ask_ai/providers/anthropic_provider.py` | 196 | Yes |
| `ask_ai/providers/azure_provider.py` | 60 | Yes |
| `ask_ai/providers/google_provider.py` | 248 | Yes |
| `ask_ai/providers/groq_provider.py` | 221 | Yes |
| `ask_ai/providers/openai_compatible_provider.py` | 123 | Yes |
| `ask_ai/providers/openai_provider.py` | 356 | Yes |
| `ask_ai/providers/openrouter_provider.py` | 130 | Yes |
| `ask_ai/py.typed` | 0 | Yes |
| `ask_ai/requirements.txt` | 6 | Yes |
| `ask_ai/router.py` | 167 | Yes |
| `ask_ai/session.py` | 145 | Yes |
| `ask_ai/structured.py` | 378 | Yes |
| `ask_ai/utils.py` | 66 | Yes |
| `assets/banner.svg` | 121 | Yes |
| `assets/features.svg` | 54 | Yes |
| `assets/resiliency.svg` | 39 | Yes |
| `docs/MIGRATION_v0.5.0.md` | 63 | Yes |
| `docs/MIGRATION_v0.6.0.md` | 79 | Yes |
| `docs/PYPI_README.md` | 149 | Yes |
| `docs/README_ar.md` | 123 | Yes |
| `docs/README_es.md` | 123 | Yes |
| `docs/README_fa.md` | 208 | Yes |
| `docs/README_ja.md` | 123 | Yes |
| `docs/README_ru.md` | 123 | Yes |
| `docs/README_tr.md` | 123 | Yes |
| `docs/README_zh.md` | 123 | Yes |
| `docs/SMOKE_TEST.md` | 57 | Yes |
| `examples/capabilities.py` | 5 | Yes |
| `examples/example_usage.py` | 66 | Yes |
| `examples/observability.py` | 18 | Yes |
| `examples/router.py` | 11 | Yes |
| `examples/secure_media.py` | 9 | Yes |
| `examples/session.py` | 5 | Yes |
| `examples/streaming_events.py` | 14 | Yes |
| `examples/structured_response.py` | 17 | Yes |
| `pyproject.toml` | 86 | Yes |
| `scripts/smoke_real.py` | 397 | Yes |
| `scripts/update_docs.py` | 20 | Yes |
| `tests/__init__.py` | 1 | Yes |
| `tests/test_capabilities.py` | 32 | Yes |
| `tests/test_core.py` | 910 | Yes |
| `tests/test_gitignore.py` | 20 | Yes |
| `tests/test_google_genai.py` | 189 | Yes |
| `tests/test_media_security.py` | 302 | Yes |
| `tests/test_native_structured.py` | 471 | Yes |
| `tests/test_observability.py` | 82 | Yes |
| `tests/test_openrouter_release.py` | 70 | Yes |
| `tests/test_openai_compatible.py` | 144 | Yes |
| `tests/test_options_validation.py` | 116 | Yes |
| `tests/test_packaging.py` | 8 | Yes |
| `tests/test_python39_compat.py` | 13 | Yes |
| `tests/test_release_docs.py` | 46 | Yes |
| `tests/test_router.py` | 60 | Yes |
| `tests/test_provider_contract.py` | 640 | Yes |
| `tests/test_session.py` | 143 | Yes |
| `tests/test_smoke_real.py` | 63 | Yes |
| `tests/test_streaming_events.py` | 104 | Yes |
| `tests/test_structured.py` | 96 | Yes |
| `tests/test_usage.py` | 359 | Yes |
| `repro/test_audit_repros.py` | 124 | Yes |
| `repro/test_library_audit.py` | 289 | Yes |
| `PROGRESS.md` | 30 | Yes |

### Reproduction method and recorded output

The reproductions use stub providers and mocked SDK clients; no network calls or API keys. Tests in `repro/` intentionally assert the *bad behavior* for unresolved findings, so a passing repro is evidence the unwanted behavior was observed, not evidence that the finding is fixed.

Recorded output after the fixes in this working tree:

```text
$ pytest -q repro
...............................                                          [100%]
31 passed, 1 warning in 3.75s
```

The warning is expected from the `image=` ignored-option probe. Before applying the relevant fixes, the initial regression repro run printed `7 failed, 1 passed`; observed failures included omitted session system prompts, session structured-output failure, dataclass default handling, `Literal` validation raising `TypeError`, shared retry-state corruption between threads, negative retries producing a fabricated network failure, and response content appearing in `repr`. The pre-fix JSON parse-error repro printed `1 failed` with the customer-secret string shown in the exception. The pre-fix media API regression printed `1 failed, 16 passed` because `ImageObject.type` was absent.

## 2. Findings

“CONFIRMED” means a deterministic local/mock reproduction observed the described result. “Fixed” means the current working tree contains the correction and a regression test. Behavioral consequences involving real vendor billing, SDK loop-affinity enforcement, or external provider semantics are separated from the locally confirmed code behavior.

### F-01 — `max_messages=1` silently erases every session turn

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/session.py:22-27`, `ConversationSession._trim`
- **Evidence / downstream impact:** The limit is rounded down to an even count (`1 -> 0`) and complete pairs are then deleted. A developer asking to retain one message instead gets an empty conversation after each request; multi-turn code silently loses context.
- **Repro output:** `test_session_max_messages_one_discards_the_entire_turn` asserted `session.messages == []` after `ask("remember me")`.
- **Patch:**
  ```diff
  -        max_pair_messages = self.max_messages - (self.max_messages % 2)
  +        if self.max_messages < 2:
  +            raise ValueError("max_messages must be at least 2 to retain a turn.")
  +        max_pair_messages = self.max_messages - (self.max_messages % 2)
  ```

### F-02 — concurrent session requests race on shared history

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/session.py:46-66`, `ConversationSession.ask`; async equivalent at `:69-89`
- **Evidence / downstream impact:** Each request snapshots `self.messages`, performs I/O, then appends the turn without synchronization. Two concurrent requests can both omit the other in-flight user prompt; a server using one session per user can generate answers from stale or inconsistent history. The same read/send/append pattern exists around `await`.
- **Repro output:** `test_session_concurrent_calls_do_not_serialize_turn_history` asserted both provider snapshots contained only their own prompt: `[['first'], ['second']]`.
- **Patch:** Serialize access per session; provide separate sync/async coordination and document that mixed sync/async concurrent access to one session is unsupported until a unified async-safe lock is designed.
  ```diff
  +        self._sync_lock = threading.RLock()
  +        self._async_lock = asyncio.Lock()
  ```
  Add regression tests that hold the provider request at a barrier and verify the second request sees the committed first turn. Do not hold a blocking threading lock across an `await`.

### F-03 — session requests used to omit the provider system prompt (**FIXED**)

- **Severity:** HIGH — **CONFIRMED, FIXED**
- **Location:** `ask_ai/session.py:40-44`, `ConversationSession._messages_for_request`
- **Evidence / downstream impact:** The previous session assembly appended only stored history and the current request, dropping the provider persona/system instruction. Session users received behavior different from the same provider’s direct `ask`.
- **Repro output:** `test_session_includes_provider_system_prompt` failed before the change; the regression now asserts the first provider message is `{"role": "system", "content": "You are a terse assistant."}`.
- **Applied patch:**
  ```diff
  +        if request_messages and request_messages[0]["role"] == "system":
  +            return [request_messages[0], *self.messages, request_messages[-1]]
  ```

### F-04 — session structured-output options were not honored (**FIXED**)

- **Severity:** HIGH — **CONFIRMED, FIXED**
- **Location:** `ask_ai/session.py:46-64` and `:69-87`
- **Evidence / downstream impact:** Session calls previously bypassed the base execution path’s response-model parsing and validation. Developers got raw responses or exceptions instead of the promised parsed type while using `session().ask(..., response_model=...)`.
- **Repro output:** `test_session_validates_structured_output` now asserts the session response parses to `User("Ada")`; it failed before the change.
- **Applied patch:** Forward `response_model` and `validation_retries` through `_execute_response` / `_execute_response_async`. Streaming sessions now reject structured validation explicitly with `NotImplementedError` rather than silently pretending to validate chunks.

### F-05 — request retry metadata was stored in shared provider instance state (**FIXED**)

- **Severity:** HIGH — **CONFIRMED, FIXED**
- **Location:** `ask_ai/base.py:134-155`, retry-count state; retry execution at `:707-812`
- **Evidence / downstream impact:** A provider instance is commonly reused in servers. A plain shared retry counter was overwritten by overlapping thread or task calls, so per-request metadata and observability could report another caller’s retries.
- **Repro output:** Thread and `asyncio.gather` probes now assert isolated values `[1, 0]`; the thread probe failed before the ContextVar change.
- **Applied patch:** Use a `ContextVar` for request-local retry state while retaining `_last_retry_count` compatibility for existing tests/callers.

### F-06 — base async streaming buffers the complete synchronous stream

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/base.py:854-859`, `BaseProvider._send_request_stream_async`
- **Evidence / downstream impact:** `list(self._send_request_stream(...))` runs to completion in a worker before the async generator yields its first chunk. On slow or unbounded streams, downstream code sees no incremental tokens, latency-to-first-token becomes full-response latency, memory grows with the response, and cancellation cannot stop the already-materializing iterator.
- **Repro output:** `test_plain_sync_stream_adapter_buffers_before_first_async_chunk` and `test_default_async_stream_fallback_yields_before_sync_source_finishes` observed `TimeoutError` while waiting for the first chunk; the sync generator had a delay between chunks.
- **Patch:** Replace `list(...)` with a bounded `queue.Queue` fed by a worker thread; forward items/errors incrementally and signal cancellation/close the source iterator when the async consumer exits. Test early `aclose()` and cancellation.

### F-07 — `providers=` fallback retries non-retryable user errors

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/base.py:352-390`, sync `ask`; similar loops in async and stream variants
- **Evidence / downstream impact:** This fallback path catches every `Exception` and advances to the next provider, even for invalid requests, authentication failures, and bad options. A typo or malformed request can trigger another provider call, hide the actionable error, and cause extra cost/data exposure.
- **Repro output:** `test_provider_fallback_retries_after_invalid_request` observed calls `["invalid", "success"]` after a `ProviderInvalidRequestError("bad user request")`.
- **Patch:**
  ```diff
  -                except Exception as e:
  +                except Exception as e:
  +                    if not self._is_retryable_error(e):
  +                        raise
  ```
  Apply consistently to sync/async/stream fallback and close any stream before deciding whether fallback is safe.

### F-08 — router fallback multiplies provider retries without a request budget

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/router.py:57-76`, `Router.ask` and `ask_async`
- **Evidence / downstream impact:** Each provider’s internal retry policy runs before the router advances. With `N` providers and `R` retries, the request can make `(R+1)*N` attempts, each potentially billable and slow; users configure provider retries but have no global attempt budget.
- **Repro output:** `test_router_retries_and_fallbacks_multiply_provider_attempts` observed six calls for two providers at `retry=2`: `["one"] * 3 + ["two"] * 3`.
- **Patch:** Add a router-level `max_attempts`/deadline budget and pass remaining attempts to each provider; stop when exhausted. Preserve provider-local retry compatibility only when the router budget is not set.

### F-09 — rate-limit `Retry-After` is ignored

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/base.py:729-730`, `:757-758`, `:782-783`, `:812-813`
- **Evidence / downstream impact:** Backoff is based only on exponential delay plus jitter. A provider’s explicit retry-after hint is discarded, potentially causing a retry during its mandated cooldown and repeated throttling.
- **Repro output:** `test_retry_after_hint_does_not_change_backoff` used `retry_after=17` and observed `delays == [2]`.
- **Patch:**
  ```diff
  -                    delay = min(2 ** attempts + random.uniform(0, 1), 30)
  +                    delay = max(float(getattr(e, "retry_after", 0) or 0),
  +                                min(2 ** attempts + random.uniform(0, 1), 30))
  ```
  Clamp to a configurable maximum and support provider-specific response headers where the SDK exposes them.

### F-10 — `timeout` is per attempt, not a total request deadline

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/base.py:707-812`; provider client timeout setup e.g. `ask_ai/providers/openai_provider.py:44-49`
- **Evidence / downstream impact:** A `timeout=0.01` configures each SDK attempt, but backoff sleeps are outside that timeout. `retry=2` used six seconds of retry delay in the mocked test; larger retries can tie up request workers far beyond the caller’s expectation.
- **Repro output:** `test_timeout_does_not_bound_retry_and_backoff_wall_clock` observed three attempts at timeout `0.01` and total scheduled sleep `6`.
- **Patch:** Compute `deadline = monotonic() + total_timeout` once; before attempts and sleeps, calculate remaining time and fail with a dedicated deadline exception when nonpositive. Pass remaining time to each provider call.

### F-11 — retries can repeat requests after a response was billed (replay confirmed; billing impact unverified)

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/base.py:713-729` and async counterpart
- **Evidence / downstream impact:** A timeout or connection loss does not prove the provider did not process the request. Retrying a generation call may bill twice or repeat external side effects. The mock confirms replay; actual billing depends on provider/request timing.
- **Repro output:** `test_retry_repeats_a_request_after_a_simulated_billed_timeout` observed two sends after a simulated “response lost after billing.”
- **Patch:** Document at-least-once semantics; add `retry_policy` with default conservative retries for ambiguous transport failures, and support idempotency keys only where a provider documents them. Never label retries exactly-once.

### F-12 — sessions are unbounded by default and have no persistence API

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/session.py:13-27`
- **Evidence / downstream impact:** `max_messages=None` is the default and `_trim()` then returns without a limit. Long-lived per-user sessions grow in memory indefinitely; serverless applications also cannot serialize/restore session state through a supported method.
- **Repro output:** Source path returns immediately for `None`; no trim occurs. No `serialize`, `restore`, or equivalent public API exists in this class.
- **Patch:** Introduce an explicit configurable default cap or require callers to select one; add `to_dict()`/`from_dict()` with versioned schema and safe role/content validation. Document that persistence stores prompts and may contain sensitive data.

### F-13 — Anthropic adapter drops the common `stop` option

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/providers/anthropic_provider.py:84-108`, `_build_kwargs`
- **Evidence / downstream impact:** `AdvancedConfig.stop` is accepted globally, but Anthropic kwargs omit `stop_sequences`. The same call changes behavior by provider and can run past a caller’s output boundary.
- **Repro output:** `test_anthropic_drops_supported_common_stop_option` asserted `"stop_sequences" not in kwargs` for `stop=["STOP"]`.
- **Patch:**
  ```diff
  +        if config.stop:
  +            kwargs["stop_sequences"] = config.stop
  ```
  Add a provider contract test for all common options and explicit unsupported-option errors.

### F-14 — Google structured-output capability contradicts native support

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/providers/google_provider.py:26` and `:102-115`, `_request_args`
- **Evidence / downstream impact:** The provider can build a native `response_schema`, yet its capabilities report `structured_output=False`. A router or downstream feature gate will exclude a provider that can serve the requested request.
- **Repro output:** `test_google_structured_capability_disagrees_with_native_schema_path` observed `False` alongside a populated `request["config"]["response_schema"]`.
- **Patch:**
  ```diff
  -        return Capabilities(streaming=True, async_streaming=True, vision=True)
  +        return Capabilities(streaming=True, async_streaming=True,
  +                            structured_output=True, vision=True)
  ```
  Confirm model/version support and report conditional capabilities if not universal.

### F-15 — `vision=True` does not mean the public request path accepts images

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/capabilities.py:5-12`; message construction in `ask_ai/base.py:665-695`
- **Evidence / downstream impact:** Capabilities advertise vision, but `ask(..., image=...)` is treated as an unknown option and `_prepare_messages` includes only the text query. The caller can receive a text answer without the intended image context.
- **Repro output:** `test_vision_capability_does_not_add_image_input_to_messages` observed `[[{"role": "user", "content": "describe this"}]]`; pytest emitted `UserWarning: Unknown option 'image'.`
- **Patch:** Add an explicit typed media input to public methods and provider message conversion; validate against `capabilities().vision` and raise a clear `MediaTypeNotSupportedError` instead of dropping the input.

### F-16 — unknown `output_type` silently becomes text generation

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/providers/openai_provider.py:75-85`, `_send_request`; equivalent provider dispatchers
- **Evidence / downstream impact:** Only `"image"` and `"audio"` are special-cased; `"video"` or a typo falls through to text. The developer’s requested output is silently ignored.
- **Repro output:** `test_unknown_output_type_falls_through_to_text_generation` observed `"text response"` and called the text method.
- **Patch:**
  ```diff
  +        if output_type not in (None, "text", "image", "audio"):
  +            raise ValueError(f"Unsupported output_type: {output_type!r}")
  ```
  Use the same validated literal/enum across providers.

### F-17 — `Response.json` promises an object but can return scalars

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/base.py:69-79`, `Response.json`
- **Evidence / downstream impact:** Its annotation is `dict | list`, while valid JSON like `"42"`, `"true"`, or `"null"` decodes to a scalar. Typed callers and static analysis believe the value supports mapping/list operations when it may not.
- **Repro output:** `test_response_json_returns_scalar_outside_its_declared_type` observed `42`.
- **Patch:** Either annotate as `Any`/a recursive JSON value type, or enforce object/list shape and raise a documented parse error; do not silently narrow the runtime contract.

### F-18 — `Response.to_model()` skips dataclass field-type validation

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/base.py:81-103`, `Response.to_model`
- **Evidence / downstream impact:** Construction from decoded JSON can instantiate a dataclass with invalid field values (e.g. `"not-an-int"` for `int`) without validation. Downstream business logic later fails or silently computes with the wrong type.
- **Repro output:** `test_to_model_dataclass_construction_skips_type_validation` observed `parsed.count == "not-an-int"`.
- **Patch:**
  ```diff
  -        return model_class(**json.loads(self.text))
  +        return parse_structured(self.text, model_class)
  ```
  Keep Pydantic v1/v2 and dataclass validation behavior covered in one contract suite.

### F-19 — an empty JSON Schema is confused with a missing response model

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/structured.py:75-92` and `ask_ai/base.py:61-67`
- **Evidence / downstream impact:** `{}` is a valid schema meaning “any JSON value,” but truthiness-based checks treat it as no model. Developers using the raw-schema feature cannot parse even a valid `{}` response.
- **Repro output:** `test_empty_json_schema_is_treated_as_missing_response_model` observed `ValueError: No response_model configured`.
- **Patch:** Use `response_model is None` for absence checks; preserve empty mappings as supplied schemas.

### F-20 — OpenAI clients have no public close/context-manager lifecycle

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/providers/openai_provider.py:42-62`
- **Evidence / downstream impact:** Sync and async HTTP clients are owned by the provider but callers have no `close`, `aclose`, or context-manager API. Repeatedly creating providers in workers/tests can retain connection pools/sockets until garbage collection.
- **Repro output:** `test_openai_provider_has_no_explicit_close_or_context_manager` asserted no lifecycle methods exist.
- **Patch:** Add `close()`, `aclose()`, `__enter__/__exit__`, and `__aenter__/__aexit__`; close only clients that were created and add leak/lifecycle tests.

### F-21 — cached async client can cross event-loop boundaries (reuse confirmed; SDK failure varies)

- **Severity:** HIGH — **CONFIRMED REUSE; IMPACT UNVERIFIED**
- **Location:** `ask_ai/providers/openai_provider.py:51-62`, `async_client`
- **Evidence / downstream impact:** The async client is cached on the provider instance with no loop ownership check. Reusing the same provider from separate `asyncio.run()` calls is common in scripts and tests; SDK transports may bind resources to the first loop and then fail/hang on another.
- **Repro output:** `test_openai_async_client_is_reused_between_event_loops` observed the same client object in both separately-created loops.
- **Patch:** Track the creating loop and raise a clear `RuntimeError` on cross-loop use, or create one async provider/client per loop; document the ownership and close requirements.

### F-22 — observability callbacks execute synchronously on the request hot path

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/observability.py:59-72`, called by `ask_ai/base.py:189-220`
- **Evidence / downstream impact:** `Observability.emit()` calls user code inline. A slow callback adds request latency and occupies the server worker; in async requests it blocks the event loop. Exceptions are suppressed, so failures are also invisible.
- **Repro output:** `test_observability_callback_runs_synchronously_on_request_path` observed the request blocked for at least 30 ms by a 30 ms hook.
- **Patch:** Define and document callback execution semantics; for async calls support awaited async hooks or queue-based delivery with bounded backpressure. Report hook failures through a safe logger/diagnostic hook.

### F-23 — fallback logging and errors include raw provider exception text

- **Severity:** HIGH — **CONFIRMED**
- **Location:** `ask_ai/base.py:352-390`, `:498-536`; `ask_ai/router.py:57-76`
- **Evidence / downstream impact:** Fallback logs include `e` and accumulated failures interpolate exception text. Provider exceptions may contain prompt fragments, user data, URLs, request IDs, or headers; logs are commonly exported to shared observability systems.
- **Repro output:** `test_fallback_log_contains_unredacted_provider_error` observed `private-prompt-fragment` in `caplog.text`.
- **Patch:** Log provider name, exception class, and safe request ID only; retain the original exception as `__cause__` for explicit debugging. Avoid including raw exception text in aggregate `ProviderError`.

### F-24 — structured-validation failure metadata double-counts transport retries

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/base.py:249-276` and failure metadata at `:205-220`
- **Evidence / downstream impact:** A transport retry followed by a validation failure reports a retry count that adds the same retry twice. Downstream billing/telemetry dashboards can overstate failures and mislead retry tuning.
- **Repro output:** `test_failed_structured_response_double_counts_retries_in_failure_metadata` observed two provider calls but `retry_count == 2`.
- **Patch:** Keep one request-local attempt counter and attach it once at the outer request boundary; validation retries and transport retries should be separate metadata fields.

### F-25 — media temp files persist until process exit

- **Severity:** MEDIUM — **CONFIRMED**
- **Location:** `ask_ai/media.py:37-66`, `TempFileManager`; callers at `:374`, `:416`, `:459`
- **Evidence / downstream impact:** Playback/export creates `delete=False` temporary files; cleanup is registered only with `atexit`. Long-running services and notebooks accumulate user media on disk until process shutdown, even after playback returns.
- **Repro output:** `test_temp_media_files_remain_tracked_until_process_cleanup` observed all three files still existing and tracked after creation.
- **Patch:** Add `remove_temp_file(path)` and `try/finally` cleanup at each synchronous consumer; provide an explicit context-managed temp export API for callers retaining files.

### F-26 — media transport relies on private httpx/httpcore internals (compatibility risk unverified)

- **Severity:** MEDIUM — **[UNVERIFIED]**
- **Location:** `ask_ai/media_security.py:117-152`
- **Evidence / downstream impact:** The DNS-pinned transport subclasses `httpcore.SyncBackend` and mutates `transport._pool._network_backend`, a private implementation detail. A supported `httpx`/`httpcore` upgrade can break media downloads at runtime despite unchanged public SDK API.
- **Repro output:** Not reproduced across multiple dependency versions; current tests pass against the installed version.
- **Patch:** Pin a tested compatibility range or use a supported transport/connector API; add a CI matrix across the minimum and newest supported `httpx`/`httpcore` versions.

### F-27 — no Windows test job despite Windows-specific media paths/processes

- **Severity:** MEDIUM — **CONFIRMED CONFIGURATION GAP**
- **Location:** `.github/workflows/ci.yml:9-40`; media playback in `ask_ai/media.py`
- **Evidence / downstream impact:** CI covers Python 3.10–3.13 but only on `ubuntu-latest`. Downstream Windows users can encounter path, subprocess, file-locking, and temporary-file cleanup differences that CI never exercises.
- **Repro output:** CI matrix has one OS value, `ubuntu-latest`; no Windows runner is declared.
- **Patch:**
  ```diff
  -    runs-on: ubuntu-latest
  +    runs-on: ${{ matrix.os }}
       strategy:
         matrix:
  +        os: [ubuntu-latest, windows-latest]
  ```
  Keep any platform-specific real-media checks mocked.

### F-28 — tests do not enforce a type-check or coverage baseline

- **Severity:** LOW — **CONFIRMED CONFIGURATION GAP**
- **Location:** `.github/workflows/ci.yml:21-40`, `pyproject.toml:74-86`
- **Evidence / downstream impact:** CI runs Ruff, pytest, build, and wheel smoke install, but no mypy/Pyright or coverage threshold. Public APIs use broad `**kwargs`; response type mismatches such as F-17 are not caught by current checks.
- **Repro output:** Complete CI workflow contains no type-check or coverage command.
- **Patch:** Add a non-blocking coverage report initially, then set a threshold after establishing a baseline; type-check public modules and examples with Pyright or mypy in CI.

### F-29 — test suite does not exercise streaming cancellation/early close and cross-loop use end-to-end

- **Severity:** MEDIUM — **CONFIRMED TEST GAP**
- **Location:** `tests/test_streaming_events.py`, `tests/test_core.py`, `tests/test_session.py`
- **Evidence / downstream impact:** Existing tests cover stream chunks and error events but not whether an underlying provider generator is closed after `break`, whether cancellation stops I/O, or whether cached clients are used across real loops. Those cases affect resource leaks and hanging async applications.
- **Repro output:** The test inventory has no assertions for generator `finally` cleanup, `aclose()`, or cancellation propagation.
- **Patch:** Add fake sync/async generators with `finally` markers; break after one chunk and assert closure. Cancel an async consumer and assert cancellation reaches provider transport.

### F-30 — secure media edge-case coverage is incomplete for hostile URL/parser variations (no bypass confirmed)

- **Severity:** MEDIUM — **[UNVERIFIED]**
- **Location:** `ask_ai/media_security.py:16-65`, `MediaPolicy._validated_addresses`
- **Evidence / downstream impact:** The implementation rejects non-HTTPS, private/reserved resolved IPs, and redirects, pins DNS addresses, and enforces streamed size limits. No exploitable bypass was confirmed in this audit, but tests do not exhaust userinfo, IDNA/case normalization, IPv4-mapped IPv6, DNS answer changes, unusual numeric IP spellings, and malformed content-length combinations. A bypass would let an attacker-driven media URL reach internal services.
- **Repro output:** Existing safe-media tests pass; the hostile-URL edge matrix was not fully executed, so this is not labeled confirmed.
- **Patch:** Add table-driven parser/DNS tests for those cases and preserve the current deny-on-any-private-answer and redirects-disabled behavior; fail closed on ambiguous URL forms.

### F-31 — no public session serialization/versioning contract

- **Severity:** LOW — **CONFIRMED**
- **Location:** `ask_ai/session.py:8-140`
- **Evidence / downstream impact:** The only history operations are append, trim, and `clear`; serverless or database-backed clients must reach into mutable `messages` and invent their own format, making future history changes a semver hazard.
- **Repro output:** No serialization or restore method exists in the complete public session class.
- **Patch:** Add versioned `ConversationSession.to_dict()` / `from_dict(provider, payload)` with schema validation and document that callers own encryption/retention.

## 3. Public API and library contract summary

- `BaseProvider.ask`, `ask_async`, `ask_stream`, and `ask_stream_async` expose `**kwargs` rather than a single typed request contract. Providers differ in what they accept and forward; this makes typos and provider-specific behavior difficult to discover. F-13, F-15, and F-16 demonstrate observable inconsistencies.
- Return shapes differ by mode: normal calls return `Response`, streams yield `str`, event streams yield typed events, and `Response.json` is more permissive than its annotation (F-17). Add overloads or explicit request/result types.
- The package does contain `ask_ai/py.typed`, and `pyproject.toml` includes it in package data. The wheel check confirmed it is present.
- Provider SDK types are mostly translated into `Response`, but unsupported features/options should be rejected explicitly rather than silently discarded.
- `Router` accepts providers directly and has no plugin-entry-point registry. The API can remain stable while adding an optional discovery mechanism later.
- Current `__version__` and `pyproject.toml` both say `0.6.0`, but they are separately maintained; make release version single-source-of-truth before automated publishing.
- No confirmed mutable default argument defect was found in the reviewed public constructors.

## 4. Concurrency, retries, streaming, sessions, and errors

- Retry counters are now ContextVar-isolated (F-05); other per-provider mutable state includes clients and middleware. Provider SDK clients should be documented as shareable only within their supported threading/event-loop model.
- `ConversationSession` mutates a shared list without locking (F-02). `Router` sorts providers from mutable profiles and provider objects; configure profiles before sharing a router and treat mutation as unsupported unless synchronization is added.
- Streaming retry loops correctly avoid retrying after yielding data, preventing duplicated prefixes. This is safer than replaying a partial stream, but callers receive a mid-stream exception and need an explicit partial-output policy.
- The base async sync-stream adapter buffers the whole result (F-06). Native async providers override it, but custom `BaseProvider` subclasses may inherit the surprising behavior.
- `asyncio.CancelledError` is not caught by `except Exception` on current Python, so it generally propagates; cancellation/underlying generator closure still needs the tests in F-29.
- Provider SDK errors are mapped in adapter calls; custom provider exceptions can pass through. The fallback paths’ raw exception interpolation remains the concrete secret/privacy risk (F-23).
- Retries are exponential with jitter but no Retry-After or total deadline. Router and provider retry counts compound. Requests may be replayed after ambiguous failures (F-08–F-11).

## 5. Structured output, media safety, and observability

- Dataclass defaults and `Literal` validation defects were corrected in `ask_ai/structured.py`; mapping, tuple, set, and bool-vs-int validation were also tightened. Regression tests cover those paths.
- `Response.to_model()` and empty raw schemas remain defects (F-18, F-19). Native schema support varies across providers and should be tested against a consistent contract, not inferred from a single adapter.
- Media downloader checks HTTPS, DNS-resolved address classes, redirects, content length and streamed size, and detected MIME type. This audit did not confirm an SSRF bypass. The private transport internals and edge-case test gaps are F-26 and F-30.
- `TempFileManager` does not delete media files at operation completion (F-25).
- Observability callback exceptions are swallowed, which prevents user hooks from breaking the request, but the callback itself is synchronous and can block requests (F-22). Failure events include `str(error)` in metadata; together with raw fallback logging this requires redaction.
- `Response.__repr__` and malformed-JSON exceptions now avoid including response content. The pre-fix repro exposed a customer string; the current tests assert redaction.

## 6. Packaging, compatibility, docs, and CI

### Verified

- Python floor is 3.10; CI matrix declares 3.10, 3.11, 3.12, and 3.13.
- `ask_ai` and `ask_ai.providers` imported from the built wheel in a fresh venv with **no** OpenAI, Anthropic, or Google SDK installed.
- `py.typed` is included in the wheel.
- `twine check` passed for the wheel and both sdist filenames. The sdist includes `pyproject.toml`, package source, and tests.
- No actual optional SDK was required to import the package.

### Remaining gaps

- Windows CI, a coverage report, a focused mypy check, and pip-audit are now configured (F-27/F-28); the final CI workflow has not yet been run on GitHub in this session.
- The clean-environment pip-audit check found no known vulnerabilities in the current resolved dependency set. This is a point-in-time scan, not a guarantee about future releases.
- Wheel smoke test uses `--no-deps`, as intended for lazy-import verification; it does not validate every optional extra combination.
- The test named `test_python39_compat.py` is not a Python 3.9 support claim: project metadata correctly sets `>=3.10`. Verify that the test’s name and intent do not mislead maintainers.
- The README/PyPI docs now describe session structured behavior and recent fixes. Provider-specific model names and pricing are intentionally not hard-coded because they change frequently.
- Error messages should consistently state which option/provider is unsupported and how to remedy it; silent option loss is the more serious issue.

## 7. Provider API verification and support matrix

Official documentation pages were fetched directly for current API shapes. Model catalogs and feature availability change frequently; the matrix reports only details present in fetched official pages and does not freeze pricing or guarantee every model/account configuration.

| Provider | API/authentication and streaming/tools shape | Current official docs |
|---|---|---|
| OpenAI | Bearer API key; Chat Completions and Responses APIs; streaming and function tools supported. | [Text generation / API docs](https://developers.openai.com/api/docs/guides/text) |
| Anthropic | `x-api-key` and `anthropic-version`; Messages API; SSE streaming and `tool_use`. | [Messages API](https://platform.claude.com/docs/en/api/messages) |
| Gemini | API key for Gemini API or Google credentials for Vertex; `generateContent` / `streamGenerateContent`; function calling and JSON schemas. | [Generate content](https://ai.google.dev/api/generate-content) |
| Mistral | API-key authentication; Chat Completions at `https://api.mistral.ai/v1/chat/completions`; current quickstart uses `mistral-large-latest`. | [API reference](https://docs.mistral.ai/api/) |
| Cohere | Bearer token; v2 `POST /v2/chat`; stream events and tools. | [Chat v2](https://docs.cohere.com/v2/reference/chat) |
| xAI | API-key authentication and OpenAI SDK base URL `https://api.x.ai/v1`; current quickstart uses the Responses API and `grok-4.7`; function calling is documented. | [xAI API docs](https://docs.x.ai/docs) |
| DeepSeek | API-key Chat Completions endpoint; docs list `deepseek-flash` and `deepseek-v4-pro`, with SSE streaming, JSON output, and function tools. | [Create chat completion](https://api-docs.deepseek.com/api/create-chat-completion) |
| Qwen / DashScope | DashScope documents an OpenAI-compatible API configured by API key, base URL, and model name; routes and feature support depend on deployment/model. | [OpenAI compatibility](https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope) |
| OpenRouter | Bearer key; `/api/v1/chat/completions` and Responses API; normalized routing, streaming, and tool calls. | [API reference](https://openrouter.ai/docs/api_reference/overview) |
| Together | Bearer key; OpenAI-compatible chat completions; streaming/tools depend on model. | [Chat completions](https://docs.together.ai/reference/chat-completions) |
| Fireworks | Bearer key; OpenAI-compatible chat completions; stream/tool support varies by model. | [Chat completions](https://docs.fireworks.ai/api-reference/post-chatcompletions) |
| Groq | Bearer key; chat completions with streaming and tool calling for supported models. | [API reference](https://console.groq.com/docs/api-reference#chat-create) |
| Azure OpenAI | API key or Microsoft Entra ID; deployment-scoped URL/version; chat/stream/tools depend on deployment and API version. | [REST API reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference) |
| AWS Bedrock | AWS SigV4/SDK credentials; `Converse`/`ConverseStream`; `toolConfig` for supported models. | [Converse](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) |
| Vertex AI | Google ADC/OAuth; `generateContent` and streaming; function calling/model features vary. | [Generative AI REST reference](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest) |
| Ollama | Local HTTP API with no authentication by default; `/api/chat` returns NDJSON streaming by default and documents structured outputs, tools, and image input. Model support varies. | [Chat API](https://docs.ollama.com/api/chat) |
| LM Studio | Local server with OpenAI-compatible endpoints; key/configuration depends on local server setup; tools/model support varies. | [OpenAI compatibility](https://lmstudio.ai/docs/developer/openai-compat) |
| vLLM | OpenAI-compatible server; auth is deployment-configured; chat streaming, structured outputs, and tools depend on server/model configuration. | [Serving docs](https://docs.vllm.ai/en/latest/serving/online_serving/) |
| llama.cpp | The current HTTP server documents OpenAI-compatible chat-completions, Responses, and embeddings routes, plus function calling and schema-constrained JSON; auth depends on deployment configuration. | [llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) |
| Generic OpenAI-compatible | Usually Bearer token or local/no auth; Chat Completions is common but not fully standardized; streaming/tools/structured output vary. | [OpenAI Chat Completions reference](https://platform.openai.com/docs/api-reference/chat/create) |

## 8. Generic OpenAI-compatible provider

Implemented in commit `3fc81d2` as `ask_ai/providers/openai_compatible_provider.py`. It accepts `base_url`, optional `api_key`, required `model`, and optional headers; validates the URL and delegates the OpenAI Chat Completions wire format through the OpenAI SDK. It does not claim support for every Responses API or vendor extension.

The class extends `OpenAIProvider`, overrides sync/async text and stream transport methods, maps SDK errors, declares conservative capabilities, and is exported from `ask_ai.providers` and `ask_ai`. `Router` accepts it like any other provider:

```python
router = Router([
    OpenAICompatibleProvider(base_url="http://localhost:8000/v1", model="served-model")
])
```

### Provider contract suite for every adapter

1. Import without unrelated SDK extras; missing own SDK raises a clear install-extra error.
2. Sync/async text return normalized `Response` and map auth, invalid request, rate-limit, timeout, and transport failures.
3. Sync/async streaming yield incrementally, preserve chunk order, close on early break, propagate cancellation, and never retry after yielded content.
4. Options (`temperature`, `top_p`, `max_tokens`, `stop`, `timeout`) are forwarded or explicitly rejected; none are silently ignored.
5. Structured output validates representative dataclass, Pydantic v1/v2, nested/optional/union/enum/Literal models, malformed/fenced/truncated JSON, and bounded validation retries.
6. Capabilities agree with actual support; unsupported media/tools fail explicitly.
7. Clients close through sync/async context managers; loop ownership is defined and tested.
8. Request and error representations/logs do not expose API keys, headers, prompts, or response bodies.

## 9. Round-one fixes and validation (historical)

The initial fixes were committed in `bddc321` with focused regression tests and related documentation updates:

1. **Session correctness:** preserve provider system prompts; support non-streaming structured responses; clearly reject structured streaming validation.
2. **Concurrency metadata:** isolate retry count per thread/task with `ContextVar`, preserving existing `_retry_count` access behavior.
3. **Structured validation:** honor omitted dataclass defaults; validate `Literal`, bool-vs-int, mappings, tuples, and sets correctly.
4. **Retry validation:** reject negative retry counts immediately with `ValueError`.
5. **Sensitive-data minimization:** remove response content from `Response.__repr__` and JSON parse exception messages.

Also fixed the closely related missing `MediaObject.type` property used by CLI/example code and added a regression test. These round-one fixes are preserved in commit `bddc321`; subsequent ordered changes are recorded in the final disposition table below.

### Validation results

```text
Baseline recorded before audit changes: 197 passed
After changes:                         203 passed, 1 warning
Mocked reproduction suite:              31 passed, 1 warning
Ruff:                                   All checks passed
python -m build --no-isolation:         exit code 0
twine check:                            freshly built wheel/sdist PASSED
Fresh venv wheel import:                passed; no OpenAI/Anthropic/Google SDK installed
wheel contents:                         py.typed present
sdist contents:                         pyproject.toml, ask_ai/base.py, and tests present
```

The single full-suite warning is the existing `safe_mode` deprecation warning. The Ruff check initially identified one import ordering issue in the added tests; it was corrected and the final Ruff run passed.

## 10. Roadmap and feature proposals

### Quick wins (remaining)

- F-01: reject or correctly handle `max_messages=1`.
- F-11: document at-least-once retry semantics and expose an explicit replay/idempotency policy.
- F-22/F-24: provide non-blocking observability hooks and accurate separate transport/validation retry metadata.
- F-25/F-26: add deterministic media temp-file cleanup and replace reliance on private httpx/httpcore internals.
- F-12/F-31: bound or persist long-lived session histories with a versioned serialization contract.

### Medium-term reliability

- F-11/F-22/F-24: safe replay policy, asynchronous hook delivery, and accurate retry metadata.
- F-25/F-26: media resource lifecycle and a supported public transport extension point.
- F-12/F-31: bounded history, serialization, and restoration.

### Strategic (next 2–3 quarters)

1. **Generic OpenAI-compatible provider** — F-14 and multi-provider gaps.
2. **Tool/function-call abstraction** — F-13/F-14; normalized tool schema and result loop.
3. **Embeddings API** — absent from current public request contract.
4. **Async batch helper** — bounded concurrency and cancellation for bulk workloads.
5. **Response caching** — opt-in, key-safe, provider/model/config-aware cache.
6. **Cost/token accounting** — normalized usage and current pricing source; never imply estimates are invoices.
7. **Rate limiter** — per-provider/per-model concurrency and token budgets.
8. **Circuit breaker** — provider health state and recovery policy layered over Router.
9. **Session persistence** — F-12/F-31, versioned serialization and restore.
10. **Typed streaming events** — stable event union for deltas, tool calls, usage, completion, and errors.
11. **Provider contract test package/fixture** — enforce the suite above for built-in and third-party adapters.
12. **CLI improvements** — configuration discovery and safe structured-output invocation.
13. **Dynamic model registry** — capabilities/context/pricing loaded from a versioned external source, not stale constants.
14. **Third-party provider entry points** — optional plugin discovery with explicit trust boundaries.
15. **Request policy layer** — deadlines, retry/idempotency policy, and sensitive-data redaction.
16. **Media lifecycle API** — context-managed temporary exports and explicit retention controls (F-25).
17. **Compatibility test matrix** — supported SDK/API versions, Python versions, Windows/Linux/macOS.

### 30 / 60 / 90 days

- **30 days:** address F-01/F-11/F-22/F-24/F-25; publish the retry, session, and resource-lifecycle policies.
- **60 days:** resolve F-26 and F-12/F-31; exercise the new Windows/type/coverage/audit CI on hosted runners.
- **90 days:** evaluate versioned session persistence, rate limiter/circuit breaker prototypes, token/cost normalization, and a tested embeddings/batch API.

## 11. Self-review

- I treated the library as a dependency embedded in other programs, not as a standalone application: findings emphasize repeated imports, shared provider/session objects, async loop ownership, retries, memory, logs, resource cleanup, and semver contracts.
- The final local validation is `458 passed, 1 warning`, with 77% statement coverage and Ruff clean. The warning is the existing `safe_mode` deprecation warning.
- The 31 original mock reproductions and the round-two regressions are not live vendor/billing tests; billing effects, real provider rate-limit headers, and hosted CI execution were not verified.
- The media edge matrix rejects userinfo and malformed/mismatched lengths; IPv4-mapped/numeric IP and DNS-pinning cases found no SSRF bypass.
- Official pages were fetched directly for the previously marked Mistral, xAI, DeepSeek, Qwen/DashScope, and llama.cpp details. Model names/features remain point-in-time documentation claims.
- Exact per-step full-suite counts for steps 2–8 were not retained in the recovered progress state and are marked as unavailable rather than reconstructed or guessed.

## 12. Final finding status and verification

Status is evaluated against the final code in this branch. `FIXED` means the listed change is committed and its named regression test passes. `OPEN` means the behavior or risk remains and the reason is stated. The descriptive evidence and patch sketches in Section 2 record the initial audit and are superseded by this table.

| Finding | Status | Evidence |
|---|---|---|
| F-01 | OPEN | `ask_ai/session.py::_trim` still rounds `max_messages=1` down to zero; `repro/test_library_audit.py::test_session_max_messages_one_discards_the_entire_turn` documents the behavior. No fixing commit. |
| F-02 | FIXED | `9c3b5ce`; `tests/test_session.py::test_session_serializes_concurrent_sync_requests` and `test_session_serializes_concurrent_async_requests`. |
| F-03 | FIXED | `bddc321`; `repro/test_audit_repros.py::test_session_includes_provider_system_prompt`. |
| F-04 | FIXED | `bddc321`; `repro/test_audit_repros.py::test_session_validates_structured_output`. |
| F-05 | FIXED | `bddc321`; `repro/test_audit_repros.py::test_retry_count_is_isolated_between_threads` and `test_retry_count_is_isolated_between_asyncio_tasks`. |
| F-06 | FIXED | `483166d`; `tests/test_core.py::test_default_async_stream_adapter_yields_first_chunk_incrementally`, `test_default_async_stream_adapter_closes_sync_source_on_early_aclose`, and `test_default_async_stream_adapter_closes_sync_source_on_cancellation`. |
| F-07 | FIXED | `c44b741`; `tests/test_core.py::test_nonretryable_request_fallback_stops_for_sync_and_async_calls`, `test_nonretryable_stream_fallback_stops_for_sync_and_async_calls`, and `test_nonretryable_bad_options_do_not_advance_provider_fallback`. |
| F-08 | FIXED | `3c3ae54`; `tests/test_router.py::test_router_max_attempts_caps_provider_attempts_and_disables_nested_retries`. |
| F-09 | FIXED | `3c3ae54`; `tests/test_core.py::test_retry_after_is_honored_and_clamped`. |
| F-10 | FIXED | `3c3ae54`; `tests/test_core.py::test_total_timeout_bounds_sync_retries_and_attempt_timeout`, `test_total_timeout_bounds_async_retries`, and `tests/test_router.py::test_router_total_deadline_is_shared_across_provider_fallbacks`. |
| F-11 | OPEN | Retries may replay a request after an ambiguous timeout/disconnect; no provider-specific idempotency/replay policy was added. Actual billing impact remains provider-dependent. |
| F-12 | OPEN | Session history remains unbounded when `max_messages=None`; no versioned persistence API was added. |
| F-13 | FIXED | `754a02d`; `tests/test_options_validation.py::test_anthropic_forwards_stop_sequences`. |
| F-14 | FIXED | `754a02d`; `tests/test_capabilities.py::test_google_structured_capability_is_true`. |
| F-15 | FIXED | `754a02d`; `tests/test_capabilities.py::test_unsupported_image_and_output_types_fail_before_provider_request`. |
| F-16 | FIXED | `754a02d`; `tests/test_capabilities.py::test_unsupported_image_and_output_types_fail_before_provider_request` and `tests/test_options_validation.py::test_unknown_output_type_fails_before_request`. |
| F-17 | FIXED | `c55e847`; `tests/test_structured.py::test_response_json_returns_typed_json_values`. |
| F-18 | FIXED | `c55e847`; `tests/test_structured.py::test_response_to_model_validates_dataclass_field_types`. |
| F-19 | FIXED | `c55e847`; `tests/test_structured.py::test_empty_json_schema_is_a_valid_response_model`. |
| F-20 | FIXED | `affbd64`; `tests/test_core.py::test_openai_provider_sync_and_async_context_managers_close_clients` and `tests/test_provider_contract.py::test_provider_contract_closes_sync_and_async_clients`. |
| F-21 | FIXED | `affbd64`; `tests/test_core.py::test_openai_async_client_rejects_cross_event_loop_reuse` and `tests/test_provider_contract.py::test_provider_contract_rejects_reuse_across_event_loops`. |
| F-22 | OPEN | Observability callbacks still execute synchronously on the request path; no async/non-blocking hook delivery was introduced. |
| F-23 | FIXED | `dd84e95`, `a9292f9`, and `f827e54`; `tests/test_observability.py::test_fallback_redacts_exception_text_and_preserves_cause` and `tests/test_provider_contract.py::test_provider_contract_error_repr_does_not_expose_prompt_or_secret`. |
| F-24 | OPEN | Transport and structured-validation retry metadata are not separated throughout all event paths; no full accounting redesign was included. |
| F-25 | OPEN | Media temporary-file cleanup remains tied to process lifetime in the affected API; no lifecycle API was added. |
| F-26 | OPEN | Pinned media transport still replaces a private httpcore network-backend field; compatibility risk is not eliminated. |
| F-27 | FIXED | `5105bbd`; `.github/workflows/ci.yml` has an Ubuntu/Windows OS matrix. Hosted GitHub execution was not available locally. |
| F-28 | FIXED | `5105bbd`; CI emits a pytest-cov report and runs the focused mypy command. Local coverage is 77%; the check is intentionally scoped to the new compatible provider because the initial whole-package mypy run reported 54 pre-existing errors across 12 files. |
| F-29 | FIXED | `483166d`, `affbd64`, and `f827e54`; incremental first-chunk, early-close, cancellation, and cross-loop tests pass, including the parametrized provider contract suite. |
| F-30 | FIXED | `a2503c4`; `tests/test_media_security.py::test_media_policy_rejects_userinfo_urls`, `test_media_policy_rejects_non_public_numeric_ip_spellings`, `test_media_policy_normalizes_idna_allowlist_hosts`, `test_media_download_connects_only_to_the_validated_dns_address`, and `test_media_download_rejects_mismatched_or_invalid_content_lengths`. No SSRF bypass was confirmed; the tests also led to rejecting userinfo and malformed/mismatched lengths. |
| F-31 | OPEN | `ConversationSession` still has no public versioned serialization/restore contract. |

### Full-suite test counts

| Step | Full-suite count |
|---|---|
| Recovered baseline after already-completed steps 2–8 | 238 passed, 1 warning |
| 1. F-23 test migration | 238 → 239 passed |
| 2. F-07 fallback eligibility | Individual before/after count not retained; included in recovered baseline |
| 3. F-06 incremental async stream | Individual before/after count not retained; included in recovered baseline |
| 4. F-08/F-09/F-10 retry budget | Individual before/after count not retained; included in recovered baseline |
| 5. F-02 session locking | Individual before/after count not retained; included in recovered baseline |
| 6. F-13/F-14/F-15/F-16 provider behavior | Individual before/after count not retained; included in recovered baseline |
| 7. F-17/F-18/F-19 response contract | Individual before/after count not retained; included in recovered baseline |
| 8. F-20/F-21 lifecycle | Individual before/after count not retained; included in recovered baseline |
| 9. OpenAI-compatible provider | 239 → 239 passed |
| 10. Provider contract suite (`f827e54`) | 239 → 408 passed |
| 11. CI quality gates | 408 → 408 passed |
| 12. SSRF edge tests | 408 → 423 passed |
| Step 10 contract-completeness follow-up (`dc2a034`) | 423 → 458 passed |
| Final | **458 passed, 1 warning** |

Final validation: `ruff check .` passed; coverage is 77%; focused mypy passed; `pip-audit` found no known vulnerabilities in a clean environment. Exact per-step counts for steps 2–8 were not preserved during recovery and are deliberately not estimated.
