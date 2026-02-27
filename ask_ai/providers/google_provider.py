from typing import List, Dict
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..base import BaseProvider, Response
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError, MediaTypeNotSupportedError


class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
            raise APIKeyError("Google API Key is missing. Set GOOGLE_API_KEY env var or pass api_key=")

        if genai is None:
            raise ProviderError("Google Generative AI library not installed. Please install 'google-generativeai'.")

        genai.configure(api_key=self.api_key)
        self.model_name = self.model  # defaulting to "gemini-1.5-flash" via base method

    def _get_api_key_env_var(self):
        return "GOOGLE_API_KEY"

    def _get_default_model(self):
        return "gemini-1.5-flash"

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:

        if output_type in ["image", "audio"]:
            raise MediaTypeNotSupportedError("Google provider currently supports text generation primarily in this library.")

        try:
            # Convert messages to Gemini format (user/model roles)
            # OpenAI: system, user, assistant
            # Gemini: user, model
            # System instruction is separate in config usually or handled specially.

            gemini_messages = []
            system_instruction = None

            for m in messages:
                role = m["role"]
                content = m["content"]
                if role == "system":
                    system_instruction = content  # Gemini 1.5 supports system instruction
                elif role == "user":
                    gemini_messages.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    gemini_messages.append({"role": "model", "parts": [content]})

            # Prepare config
            generation_config = genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
            )

            # Initialize model
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )

            # Chat Session or Generate Content?
            # For simplicity, use start_chat with history if message list > 1, or generate_content if 1?
            # Actually, to maintain context, use chat.
            # But here we are stateless per request (user passed history in messages).
            # So `start_chat(history=...)` then send last message.

            if not gemini_messages:
                return Response(text="")

            last_msg = gemini_messages[-1]
            history = gemini_messages[:-1]

            chat = model.start_chat(history=history)
            response = chat.send_message(last_msg["parts"][0], generation_config=generation_config)

            return Response(text=response.text)

        except Exception as e:
            raise ProviderError(f"Google API Error: {e}")
