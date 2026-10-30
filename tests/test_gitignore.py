from pathlib import Path


def test_gitignore_does_not_hide_project_tests_or_root_media():
    gitignore = (Path(__file__).parents[1] / ".gitignore").read_text(encoding="utf-8")

    assert "\ntest_*.py\n" not in gitignore
    assert "\n*.png\n" not in gitignore
    assert "\n*.mp3\n" not in gitignore
    assert "local_artifacts/test_*.py" in gitignore
    assert "examples/output/*.png" in gitignore
    assert "examples/output/*.mp3" in gitignore
