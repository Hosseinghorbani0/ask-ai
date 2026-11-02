from pathlib import Path


def test_readmes_document_optional_provider_extras():
    readme = Path("README.md").read_text(encoding="utf-8")
    pypi_readme = Path("docs/PYPI_README.md").read_text(encoding="utf-8")

    assert 'pip install "askai-python[openai,groq]"' in readme
    for extra in ("openai", "anthropic", "google", "groq"):
        assert f"askai-python[{extra}]" in readme
        assert f"askai-python[{extra}]" in pypi_readme


def test_pypi_readme_matches_google_media_and_session_support():
    pypi_readme = Path("docs/PYPI_README.md").read_text(encoding="utf-8")

    assert "| **Google** | `Google` | Text, Vision |" in pypi_readme
    assert "Images, Video, Audio" not in pypi_readme
    assert "## Conversation Sessions" in pypi_readme
    assert "Memory buffer / session-based conversation management" not in pypi_readme
