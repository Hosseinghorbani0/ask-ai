from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class TextDelta:
    text: str
    index: int


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: Any
    call_id: Optional[str] = None


@dataclass(frozen=True)
class UsageUpdate:
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


@dataclass(frozen=True)
class Completed:
    response: Any
    usage: Optional[UsageUpdate] = None


@dataclass(frozen=True)
class Error:
    error: Exception
    emitted_chunks: int


def text_from_event(event: Any) -> Optional[str]:
    """Return text for legacy stream adapters, or None for non-text events."""
    if isinstance(event, TextDelta):
        return event.text
    return None
