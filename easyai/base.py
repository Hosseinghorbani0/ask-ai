from typing import Optional, Union, List, Dict, Any
import os
from .config import AdvancedConfig
from .media import ImageObject, AudioObject
from .exceptions import APIKeyError

class Response:
    """
    Unified response object for all easyai requests.
    """
    def __init__(self, text: str = "", media: Union[ImageObject, AudioObject, None] = None):
        self.text = text
        self.media = media

    def __str__(self):
        return self.text

    def save(self, path: str):
        """Smart save based on content type."""
        if self.media:
            self.media.save(path)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text)
            print(f"Text saved to {path}")

class BaseProvider:
    """
    Abstract base class for all AI providers.
    Implements the core 'ask' logic and configuration management.
    """
    def __init__(self, api_key: str = None, model: str = None, persona: str = None, **kwargs):
        # 1. Zero-Config: Try env var if key not provided
        self.api_key = api_key or os.environ.get(self._get_api_key_env_var())
        if not self.api_key:
             # Some providers might not need it (e.g. local), but generally they do.
             # We allow subclass to handle granular validation, but warn here.
             pass

        self.model = model or self._get_default_model()
        self.persona = persona
        
        # Global Advanced Config
        self.config = AdvancedConfig(**kwargs)

    def _get_api_key_env_var(self) -> str:
        """Subclasses should return the env var name, e.g. 'OPENAI_API_KEY'"""
        raise NotImplementedError

    def _get_default_model(self) -> str:
        """Subclasses should return a default model"""
        raise NotImplementedError

    def advanced(self, **kwargs):
        """
        Update global advanced settings for this instance.
        Merges new settings with existing ones.
        """
        new_conf = AdvancedConfig(**kwargs)
        # primitive merge: update self.config with new values
        for k, v in new_conf.__dict__.items():
            if v is not None:
                setattr(self.config, k, v)
        
        # Handle extra kwargs
        if new_conf.extra:
            self.config.extra.update(new_conf.extra)

    def ask(self, query: str, **kwargs) -> Response:
        """
        The main entry point. 
        Detects intent, manages config, and returns a unified Response.
        """
        # 1. Merge Request Config with Global Config
        request_config = AdvancedConfig(**kwargs)
        final_config = self._merge_configs(self.config, request_config)

        # 2. Add System/Persona Message
        messages = self._prepare_messages(query, final_config)

        # 3. Check for specific output_type override (e.g. user forced image)
        output_type = kwargs.get('output_type')
        
        # 4. Call Provider Implementation
        return self._send_request(messages, final_config, output_type)

    def _merge_configs(self, global_conf: AdvancedConfig, req_conf: AdvancedConfig) -> AdvancedConfig:
        return global_conf.merge(req_conf) # We need to implement merge logic in AdvancedConfig properly or here

    def _prepare_messages(self, query: str, config: AdvancedConfig) -> List[Dict[str, str]]:
        messages = []
        if config.system_message:
            messages.append({"role": "system", "content": config.system_message})
        elif self.persona:
            messages.append({"role": "system", "content": self.persona})
        
        messages.append({"role": "user", "content": query})
        return messages

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        """Subclasses must implement this."""
        raise NotImplementedError

    # --- Tool Definitions for Smart Intent ---
    def _get_media_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "Generate an image based on a prompt. Use this when the user asks to draw, create, or show an image.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The detailed description of the image to generate."
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_speech",
                    "description": "Generate audio speech from text. Use this when the user asks to say something, speak, or read aloud.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to speak."
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
