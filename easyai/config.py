from typing import Optional, Dict, Any

class AdvancedConfig:
    """
    Configuration class for advanced AI settings.
    """
    def __init__(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[list] = None,
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
        self.stop = stop
        
        # Smart Aliases for 10/10 Usability
        # If user passes 'prompt' or 'system', treat it as 'system_message'
        if system_message is None:
            system_message = kwargs.get("prompt") or kwargs.get("system")
        
        self.system_message = system_message
        self.safe_mode = safe_mode
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to a dictionary, filtering None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None and k != 'extra'}

    def merge(self, other_config: 'AdvancedConfig') -> 'AdvancedConfig':
        """Merge another config into this one (other overrides self)."""
        new_config = AdvancedConfig()
        # Copy self
        for k, v in self.__dict__.items():
            setattr(new_config, k, v)
        
        # Override with other
        for k, v in other_config.__dict__.items():
            if v is not None:
                setattr(new_config, k, v)
        
        return new_config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedConfig':
        return cls(**data)
