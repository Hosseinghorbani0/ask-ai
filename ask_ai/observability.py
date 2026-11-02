from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class Usage:
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


def usage_from_fields(
    source: Any,
    input_field: str,
    output_field: str,
    total_field: Optional[str] = None,
) -> Optional[Usage]:
    """Normalize provider-specific token usage fields without inventing missing counts."""
    if source is None:
        return None

    def field(name: Optional[str]) -> Optional[int]:
        if name is None:
            return None
        if isinstance(source, dict):
            return source.get(name)
        return getattr(source, name, None)

    input_tokens = field(input_field)
    output_tokens = field(output_field)
    total_tokens = field(total_field)
    if input_tokens is None and output_tokens is None and total_tokens is None:
        return None
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    return Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
    )


@dataclass(frozen=True)
class ResponseMetadata:
    provider: str
    model: str
    latency_ms: float
    retry_count: int
    usage: Optional[Usage] = None
    estimated_cost: Optional[float] = None
    failure_reason: Optional[str] = None


class Observability:
    """Optional request observability middleware."""

    def __init__(
        self,
        on_event: Optional[Callable[[dict[str, Any]], None]] = None,
        pricing: Optional[dict[str, dict[str, float]]] = None,
    ):
        self.on_event = on_event
        self.pricing = pricing or {}

    def emit(self, event: dict[str, Any]) -> None:
        if self.on_event is None:
            return
        try:
            self.on_event(event)
        except Exception:
            return

    def cost(self, model: str, usage: Optional[Usage]) -> Optional[float]:
        if isinstance(usage, dict):
            usage = Usage(**usage)
        if usage is None or model not in self.pricing:
            return None
        prices = self.pricing[model]
        if usage.input_tokens is None or usage.output_tokens is None:
            return None
        return (
            usage.input_tokens * prices.get("input", 0.0)
            + usage.output_tokens * prices.get("output", 0.0)
        ) / 1_000_000
