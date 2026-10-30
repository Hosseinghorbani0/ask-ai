import re
from pathlib import Path


def test_package_has_no_pep604_union_annotations():
    package_root = Path(__file__).parents[1] / "ask_ai"
    union_annotation = re.compile(r"\b(?:dict|list|set|tuple|str|int|float|bool)\[[^\n]*\]\s*\|\s*")
    optional_annotation = re.compile(r"\b(?:str|int|float|bool|bytes|object)\s*\|\s*None")

    for path in package_root.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert not union_annotation.search(source), path
        assert not optional_annotation.search(source), path
