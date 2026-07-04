from typing import Optional, Dict, Any, List


class AdvancedConfig:
    """
    Configuration class for advanced AI settings.
    Supports both direct init and aliased parameters for usability.
    """
    def __init__(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        system_message: Optional[str] = None,
        safe_mode: bool = False,
        **kwargs
    ):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop

        # Smart Aliases for 10/10 Usability
        # If user passes 'prompt' or 'system', treat it as 'system_message'
        if system_message is None:
            system_message = kwargs.pop("prompt", None) or kwargs.pop("system", None)
        else:
            # Remove aliases from kwargs if system_message was explicitly set
            kwargs.pop("prompt", None)
            kwargs.pop("system", None)

        self.system_message = system_message
        self.safe_mode = safe_mode
        self.extra: Dict[str, Any] = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to a dictionary, filtering None values."""
        result = {}
        for k, v in self.__dict__.items():
            if k == 'extra':
                continue
            if v is not None:
                result[k] = v
        return result

    def merge(self, other: 'AdvancedConfig') -> 'AdvancedConfig':
        """
        Merge another config into this one (other overrides self).
        Returns a new AdvancedConfig without mutating either input.
        """
        merged = AdvancedConfig()

        # Copy self values
        for k, v in self.__dict__.items():
            if k == 'extra':
                continue
            setattr(merged, k, v)

        # Override with other values (only non-None)
        for k, v in other.__dict__.items():
            if k == 'extra':
                continue
            if v is not None:
                setattr(merged, k, v)

        # Deep merge extra dicts
        merged_extra = dict(self.extra)
        merged_extra.update(other.extra)
        merged.extra = merged_extra

        return merged

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedConfig':
        """Create an AdvancedConfig from a dictionary."""
        return cls(**data)
