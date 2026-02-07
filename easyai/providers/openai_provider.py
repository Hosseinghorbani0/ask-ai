import os
import json
import requests
from typing import List, Dict, Any, Optional
import openai
from ..base import BaseProvider, Response
from ..media import ImageObject, AudioObject
from ..config import AdvancedConfig
from ..exceptions import APIKeyError, ProviderError

class OpenAIProvider(BaseProvider): # Renamed to avoid name collision in imports
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        if not self.api_key:
             raise APIKeyError("OpenAI API Key is missing. Set OPENAI_API_KEY env var or pass api_key=")
        
        self.client = openai.OpenAI(api_key=self.api_key)

    def _get_api_key_env_var(self):
        return "OPENAI_API_KEY"

    def _get_default_model(self):
        return "gpt-4o"

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        """
        Handles the logic for OpenAI API.
        Prioritizes:
        1. Explicit output_type (image/audio)
        2. Text generation (with function calling for smart intent)
        """
        
        # 1. Explicit Image
        if output_type == "image":
            return self._generate_image(messages, config)
            
        # 2. Explicit Audio
        if output_type == "audio":
            return self._generate_audio(messages, config)

        # 3. Text / Smart Intent
        return self._generate_text_or_smart(messages, config)

    def _generate_text_or_smart(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
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
                "tools": self._get_media_tools(),
                "tool_choice": "auto" 
            }
            # Filter None
            kwargs = {k: v for k, v in kwargs.items() if v is not None}

            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message

            # Check for tool calls (Smart Intent)
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                if function_name == "generate_image":
                    print(f"[Smart Intent] Detecting Image Generation: {arguments.get('prompt')}")
                    # Recursively call image gen with the prompt
                    return self._generate_image([{"role": "user", "content": arguments.get("prompt")}], config)
                
                elif function_name == "generate_speech":
                    print(f"[Smart Intent] Detecting Speech Generation")
                    return self._generate_audio([{"role": "user", "content": arguments.get("text")}], config)

            # Normal Text Response
            return Response(text=message.content)

        except Exception as e:
            raise ProviderError(f"OpenAI API Error: {e}")

    def _generate_image(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
        # Extract prompt from last user message
        prompt = messages[-1]["content"]
        try:
            response = self.client.images.generate(
                model="dall-e-3", # Defaulting to d3
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            # Download image bytes
            img_data = requests.get(image_url).content
            
            return Response(
                text=f"Generated image for: {prompt}",
                media=ImageObject(img_data)
            )
        except Exception as e:
            raise ProviderError(f"OpenAI Image Error: {e}")

    def _generate_audio(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Response:
        text = messages[-1]["content"]
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            # response.content gives bytes
            return Response(
                text=f"Generated audio for: {text}",
                media=AudioObject(response.content)
            )
        except Exception as e:
            raise ProviderError(f"OpenAI Audio Error: {e}")
