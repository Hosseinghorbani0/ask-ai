import re
import json
from typing import Dict, Any, Union

def clean_markdown(text: str) -> str:
    """Removes markdown code blocks like ```json ... ```"""
    text = text.strip()
    if text.startswith("```"):
        # find the first newline
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline+1:]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()

def extract_code(text: str) -> str:
    """Extracts code blocks from text, ignoring conversational filler."""
    text = str(text)
    matches = re.findall(r'```(?:[\w]*\n)?(.*?)```', text, re.DOTALL)
    if matches:
        return "\n\n".join(m.strip() for m in matches)
    return text

def strip_tags(text: str) -> str:
    """Removes XML/HTML tags, including <think>...</think> blocks."""
    # First remove <think>...</think> entirely if we don't want the thought process
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Remove any other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def parse_json(text: str) -> Union[Dict[str, Any], list]:
    """Tries to parse JSON from text, employing cleaning if necessary."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = clean_markdown(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            from .exceptions import AskAIParsingError
            raise AskAIParsingError(f"Failed to parse JSON: {e}\nContent snippet: {text[:100]}...")
