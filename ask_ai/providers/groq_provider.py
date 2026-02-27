from typing import List, Dict
try:
    from groq import Groq
except ImportError:
    Groq = None

from ..base import BaseProvider, Response
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError, MediaTypeNotSupportedError


class GroqProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("Groq API Key is missing. Set GROQ_API_KEY env var or pass api_key=")

        if Groq is None:
            raise ProviderError("Groq client library not installed. Please install 'groq' package.")

        self.client = Groq(api_key=self.api_key)

    def _get_api_key_env_var(self):
        return "GROQ_API_KEY"

    def _get_default_model(self):
        return "llama3-8b-8192"

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:

        # Groq currently mainly text + tool use.
        if output_type in ["image", "audio"]:
            raise MediaTypeNotSupportedError(f"Groq provider currently does not support {output_type} generation.")

        try:
            # Prepare args
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
                # Groq supports OpenAI-style tools
                "tools": self._get_media_tools(),
                "tool_choice": "auto"
            }
            # Filter None
            kwargs = {k: v for k, v in kwargs.items() if v is not None}

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            # Smart Intent Check
            if message.tool_calls:
                # Logic to handle tool calls?
                # Since Groq doesn't generate images natively, it can't "do" the action itself unless we bridge it?
                # Actually, for a *client library*, if the model says "call generate_image",
                # we technically CAN'T fulfill it if strict to "Groq Provider".
                # BUT, the user might want Groq to *decide* and then use another backend?
                # No, that breaks simple "provider" model.
                # So we should just say "I can't do that".
                # OR, we return the tool call as text?
                # For now, let's catch it and say "Groq wanted to create media but can't".
                tool_call = message.tool_calls[0]
                op = tool_call.function.name
                if op in ["generate_image", "generate_speech"]:
                    return Response(text=f"[System] The model attempted to generate {op} "
                                         f"but Groq provider does not support media generation.")

            return Response(text=message.content)

        except Exception as e:
            raise ProviderError(f"Groq API Error: {e}")
