from pathlib import Path


def test_typed_package_marker_is_included_in_package_data():
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert Path("ask_ai/py.typed").is_file()
    assert '"ask_ai" = ["py.typed"]' in pyproject
