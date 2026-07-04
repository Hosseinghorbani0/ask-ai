import re
import json
from typing import Dict, Any, List, Union


# Pre-compiled regex patterns for performance
_CODE_BLOCK_RE = re.compile(r'```(?:[\w]*\n)?(.*?)```', re.DOTALL)
_THINK_BLOCK_RE = re.compile(r'<think>.*?</think>', re.DOTALL)
_HTML_TAG_RE = re.compile(r'<[^>]+>')
_JSON_BLOCK_RE = re.compile(r'```(?:json)?\s*\n?([\s\S]*?)```')


def clean_markdown(text: str) -> str:
    """Removes markdown code blocks like ```json ... ```"""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def extract_code(text: str) -> str:
    """Extracts code blocks from text, ignoring conversational filler."""
    text = str(text)
    matches = _CODE_BLOCK_RE.findall(text)
    if matches:
        return "\n\n".join(m.strip() for m in matches)
    return text


def strip_tags(text: str) -> str:
    """Removes XML/HTML tags, including <think>...</think> blocks."""
    text = _THINK_BLOCK_RE.sub('', text)
    text = _HTML_TAG_RE.sub('', text)
    return text.strip()


def parse_json(text: str) -> Union[Dict[str, Any], List[Any]]:
    """Tries to parse JSON from text, employing cleaning if necessary."""
    # Direct parse
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try cleaning markdown wrappers
    cleaned = clean_markdown(text)
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try extracting JSON from code blocks
    match = _JSON_BLOCK_RE.search(text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except (json.JSONDecodeError, TypeError):
            pass

    from .exceptions import AskAIParsingError
    raise AskAIParsingError(
        f"Failed to parse JSON from response.\n"
        f"Content snippet: {text[:200]}..."
    )
