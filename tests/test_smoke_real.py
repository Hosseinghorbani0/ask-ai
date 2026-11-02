import json

from scripts.smoke_real import (
    PROVIDER_CHECKS,
    PROVIDER_SPECS,
    _safe_error,
    run_smoke,
)


def test_smoke_script_skips_cleanly_when_no_provider_keys_are_set(tmp_path):
    report_path = tmp_path / "smoke_report.json"
    results = run_smoke(env={}, report_path=report_path)

    assert len(results) == len(PROVIDER_SPECS) * len(PROVIDER_CHECKS) + 1
    assert all(result["status"] == "SKIP" for result in results)
    assert report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"] == {"PASS": 0, "FAIL": 0, "SKIP": len(results)}


def test_smoke_exception_text_redacts_provider_keys():
    secret = "sk-test-secret-value-123456"

    message = _safe_error(
        RuntimeError(f"request failed with {secret}"),
        {"OPENAI_API_KEY": secret},
    )

    assert secret not in message
    assert "[REDACTED]" in message
