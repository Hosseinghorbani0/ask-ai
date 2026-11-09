import re
from pathlib import Path


def test_readmes_document_optional_provider_extras():
    readme = Path("README.md").read_text(encoding="utf-8")
    pypi_readme = Path("docs/PYPI_README.md").read_text(encoding="utf-8")

    assert 'pip install "askai-python[openai,groq]"' in readme
    for extra in ("openai", "anthropic", "google", "groq"):
        assert f"askai-python[{extra}]" in readme
        assert f"askai-python[{extra}]" in pypi_readme


def test_pypi_readme_documents_current_provider_and_media_support():
    pypi_readme = Path("docs/PYPI_README.md").read_text(encoding="utf-8")

    assert "| Google Gen AI | `Google` | `google` | `GOOGLE_API_KEY` | `gemini-2.0-flash` |" in pypi_readme
    assert "vision input" in pypi_readme
    assert "## Async, media, sessions, and lifecycle" in pypi_readme
    assert "MediaPolicy" in pypi_readme


def test_publish_workflow_is_gated_on_published_releases_and_tests():
    workflow = Path(".github/workflows/publish.yml").read_text(encoding="utf-8")

    assert "release:" in workflow
    assert "types: [published]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "allow_prerelease:" in workflow
    assert "needs: [release_info, test]" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "inputs.allow_prerelease" in workflow
    assert "PYPI_API_TOKEN" in workflow
    action_shas = re.findall(r"^\s+- uses: [^@\s]+@([0-9a-f]+)$", workflow, re.MULTILINE)
    assert action_shas and all(len(sha) == 40 for sha in action_shas)


def test_ci_checks_feature_pushes_and_built_wheel():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert 'branches: ["master", "main", "feat/**"]' in workflow
    assert "python -m build" in workflow
    assert "python -m twine check dist/*" in workflow
    assert "wheel-smoke" in workflow
    assert "ask-ai" in workflow
