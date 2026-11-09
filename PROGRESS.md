# Round-two audit progress

Branch: `audit/round-2`

| Step | Status | Commit / evidence |
|---|---|---|
| 1. F-23 redaction | Done | `dd84e95` implementation; `a9292f9` moved regression into `tests/test_observability.py`; 239 passed. Split into recovery sub-commits. |
| 2. F-07 fallback eligibility | Done | `c44b741`; sync, async, and stream fallback tests. |
| 3. F-06 incremental async stream | Done | `483166d`; first chunk, early close, and cancellation tests. |
| 4. F-08/F-09/F-10 retry budget | Done | `3c3ae54`; deadline, Retry-After, and router attempt budget tests. |
| 5. F-02 session locking | Done | `9c3b5ce`; sync and async serialization tests. |
| 6. F-13/F-14/F-15/F-16 provider options | Done | `754a02d`; capability, stop, media, and output-type tests. |
| 7. F-17/F-18/F-19 response contract | Done | `c55e847`; JSON values, validation, and empty schema tests. |
| 8. F-20/F-21 provider lifecycle | Done | `affbd64`; context-manager and cross-loop tests. |
| 9. OpenAI-compatible provider | Done | `3fc81d2`; mocked tests cover four transport paths and package exports. |
| 10. Provider contract suite | Done | `f827e54`, completed by `dc2a034`; 204 parametrized provider cases cover all eight checks, including nested/union/optional/enum/Literal and Pydantic compatibility; full suite now 458 passed. |
| 11. CI quality gates | Done | `5105bbd`; Windows matrix, 77% coverage, focused mypy, and pip-audit (0 known vulnerabilities in a clean environment). |
| 12. SSRF edge tests | Done | `a2503c4`; `tests/test_media_security.py` has 32 focused cases; full suite rose from 408 to 423. URL userinfo and malformed/mismatched Content-Length are rejected; numeric-IP and DNS-pinning cases found no bypass. |

Baseline after recovery: 238 passed, 1 warning. After F-23 test migration:
239 passed, 1 warning. Ruff passes after correcting the interrupted provider
export import ordering.

After step 9: 239 passed, 1 warning; 7 focused OpenAI-compatible tests passed.
After step 10: 408 passed, 1 warning; the 169 parametrized provider contract
cases pass. Ruff passes.
After step 11: 408 passed, 1 warning; coverage is 77%, focused mypy passes,
and pip-audit reports no known vulnerabilities in a fresh environment. Ruff
passes.
After step 12: 423 passed, 1 warning; 32 media security tests pass and Ruff
passes. In the recovered record, exact full-suite counts were not retained for
steps 2-8; they are not inferred here.
After the step 10 contract-coverage follow-up: 458 passed, 1 warning; final
coverage remains 77%.
