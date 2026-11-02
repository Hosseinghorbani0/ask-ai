# Real-provider smoke test

The smoke test is an optional integration check and is intentionally not run by
the test suite. It sends small requests to real provider APIs and can incur
charges. Use only keys and accounts you are authorized to use.

## Configure keys

Set one or more environment variables. Providers without a key are skipped:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `GROQ_API_KEY`
- `OPENROUTER_API_KEY`

For example, in PowerShell:

```powershell
$env:OPENAI_API_KEY = "..."
$env:GROQ_API_KEY = "..."
```

Install the optional SDKs for the providers you want to test, plus Pydantic for
the structured-output check:

```powershell
python -m pip install "askai-python[all]"
```

## Run

From the repository root:

```powershell
python scripts/smoke_real.py
```

The script prints a PASS/FAIL/SKIP table and writes `smoke_report.json` in the
current directory. It never prints API keys and replaces key-shaped values in
reported exception text. The JSON report contains check names, status, and
sanitized details only.

For each configured provider, the script checks a text request, sync streaming,
async request and streaming (including first-chunk latency), structured output
with validation retries, token usage and missing-cost behavior, fallback from
an invalid key to a valid provider, two-turn session context, and a one-second
timeout. Router routing with static reliability profiles is checked when at least
two providers are configured.
Small output limits and inexpensive model IDs are used. The current model IDs
are listed in `scripts/smoke_real.py`.

The script itself has unit coverage for the no-key skip path. Provider results
from this script are real API evidence; mock-based unit tests do not guarantee
that a live provider accepts a model or request option.
