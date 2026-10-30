from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Capabilities:
    text: bool = True
    streaming: bool = False
    async_streaming: bool = False
    structured_output: bool = False
    tool_calls: bool = False
    image_generation: bool = False
    audio_generation: bool = False
    vision: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
