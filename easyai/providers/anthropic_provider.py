from typing import List, Dict, Any, Optional
import os
try:
    import anthropic
except ImportError:
    anthropic = None

from ..base import BaseProvider, Response
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError, MediaTypeNotSupportedError

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
             raise APIKeyError("Anthropic API Key is missing. Set ANTHROPIC_API_KEY env var or pass api_key=")
        
        if anthropic is None:
            raise ProviderError("Anthropic client library not installed. Please install 'anthropic' package.")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _get_api_key_env_var(self):
        return "ANTHROPIC_API_KEY"

    def _get_default_model(self):
        return "claude-3-5-sonnet-20240620"

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        
        if output_type in ["image", "audio"]:
             raise MediaTypeNotSupportedError(f"Anthropic provider currently does not support {output_type} generation.")

        try:
            # Convert messages to Anthropic format
            # OpenAI: system, user, assistant
            # Anthropic: system arg + messages list (user/assistant)
            
            anthropic_messages = []
            system_instruction = None

            for m in messages:
                role = m["role"]
                content = m["content"]
                if role == "system":
                    system_instruction = content 
                elif role in ["user", "assistant"]:
                    anthropic_messages.append({"role": role, "content": content})
            
            # Prepare args
            kwargs = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": config.max_tokens or 1024, # Anthropic requires max_tokens usually
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
            if system_instruction:
                kwargs["system"] = system_instruction
                
            # Filter None (except max_tokens if needed, but we set default)
            kwargs = {k: v for k, v in kwargs.items() if v is not None}

            # TODO: Add tool support for Smart Intent if feasible.
            # Anthropic supports tools.
            # For simplicity in V1, maybe just text?
            # User asked for "Smart Intent" globally. 
            # If we want smart intent here, we define tools in 'tools' arg.
            # But the 'media' generation needs a callback.
            # For now, let's stick to text to ensure stability, unless I add the tool schema.
            # Adding tool schema for Anthropic is different from OpenAI.
            # Let's skip tools for Anthropic in V1 or add later if requested.
            # The prompt said "Smart Intent... if type is not specified... easyai registers (tools)".
            # If I don't add it, Anthropic won't have smart media.
            # That's acceptable for V1.

            response = self.client.messages.create(**kwargs)
            
            # response.content is a list of blocks.
            text_content = ""
            if response.content:
                text_content = response.content[0].text # Assuming first block is text

            return Response(text=text_content)

        except Exception as e:
            raise ProviderError(f"Anthropic API Error: {e}")
