import os
import time
import random
import asyncio
import logging
from typing import Union, List, Dict, Any, Iterator, AsyncIterator

from .config import AdvancedConfig
from .media import ImageObject, AudioObject

logger = logging.getLogger("ask_ai")


class Response:
    """
    Unified response object for all ask-ai requests.
    """
    def __init__(self, text: str = "", media: Union[ImageObject, AudioObject, None] = None, response_model: Any = None, **kwargs):
        self._raw_text = text
        self.media = media
        self.response_model = response_model
        self._kwargs = kwargs

    @property
    def text(self) -> str:
        text = self._raw_text
        if self._kwargs.get('strip'):
            from .utils import strip_tags
            text = strip_tags(text)
        if self._kwargs.get('clean'):
            from .utils import clean_markdown
            text = clean_markdown(text)
        if self._kwargs.get('code'):
            from .utils import extract_code
            text = extract_code(text)
        return text

    @property
    def json(self) -> Union[Dict[str, Any], list]:
        """Returns parsed JSON. If 'json=True' was passed, this is highly reliable."""
        from .utils import parse_json
        return parse_json(self._raw_text)

    @property
    def pydantic(self) -> Any:
        """Returns parsed Pydantic model instance if response_model was provided."""
        if not self.response_model:
            raise ValueError("No response_model was specified for this request.")
        return self.to_model(self.response_model)

    def to_model(self, model_class: Any) -> Any:
        """Parse the response text into a specified Pydantic model."""
        text_content = self.text
        if hasattr(model_class, "model_validate_json"):
            return model_class.model_validate_json(text_content)
        elif hasattr(model_class, "parse_raw"):
            return model_class.parse_raw(text_content)
        else:
            import json
            data = json.loads(text_content)
            return model_class(**data)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        preview = self._raw_text[:80] + "..." if len(self._raw_text) > 80 else self._raw_text
        return f'<Response text="{preview}">'

    def save(self, path: str) -> None:
        """Smart save based on content type."""
        if self.media:
            self.media.save(path)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text)


class BaseProvider:
    """
    Abstract base class for all AI providers.
    Implements the core 'ask' logic and configuration management.
    """
    def __init__(self, api_key: str = None, model: str = None, persona: str = None, **kwargs):
        # Zero-Config: Try env var if key not provided
        self.api_key = api_key or os.environ.get(self._get_api_key_env_var())
        self.model = model or self._get_default_model()
        self.persona = persona
        self.config = AdvancedConfig(**kwargs)

    def _get_api_key_env_var(self) -> str:
        """Subclasses should return the env var name, e.g. 'OPENAI_API_KEY'"""
        raise NotImplementedError

    def _get_default_model(self) -> str:
        """Subclasses should return a default model"""
        raise NotImplementedError

    def advanced(self, **kwargs) -> None:
        """
        Update global advanced settings for this instance.
        Merges new settings with existing ones.
        """
        new_conf = AdvancedConfig(**kwargs)
        for k, v in new_conf.__dict__.items():
            if k == 'extra':
                continue
            if v is not None:
                setattr(self.config, k, v)
        if new_conf.extra:
            self.config.extra.update(new_conf.extra)

    # ─── Sync API ───────────────────────────────────────────

    def ask(self, query: str, **kwargs) -> Response:
        """
        The main entry point. Sync version.
        Detects intent, manages config, and returns a unified Response.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        errors.append(f"{p.__name__} init failed: {e}")
                        continue
                else:
                    p_inst = p
                try:
                    return p_inst.ask(query, **kwargs)
                except Exception as e:
                    errors.append(f"{p_inst.__class__.__name__}: {e}")
                    logger.warning("Provider fallback failed for %s: %s", p_inst.__class__.__name__, e)
            from .exceptions import ProviderError
            raise ProviderError(f"All fallback providers failed: {errors}")

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        output_type = kwargs.get('output_type')
        retry = int(kwargs.get('retry', final_config.extra.get('retry', 0)) or 0)
        response_model = kwargs.get('response_model')

        response = self._execute_with_retry(
            self._send_request, messages, final_config, output_type, retry
        )
        if response_model:
            response.response_model = response_model
        return response

    def ask_stream(self, query: str, **kwargs) -> Iterator[str]:
        """
        Streaming text generation. Yields text chunks.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        errors.append(f"{p.__name__} init failed: {e}")
                        continue
                else:
                    p_inst = p
                try:
                    yield from p_inst.ask_stream(query, **kwargs)
                    return
                except Exception as e:
                    errors.append(f"{p_inst.__class__.__name__}: {e}")
                    logger.warning("Provider fallback failed for %s: %s", p_inst.__class__.__name__, e)
            from .exceptions import ProviderError
            raise ProviderError(f"All fallback providers failed: {errors}")

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        yield from self._send_request_stream(messages, final_config)

    # ─── Async API ──────────────────────────────────────────

    async def ask_async(self, query: str, **kwargs) -> Response:
        """
        Native async version of ask().
        Uses provider's async client directly — no thread pool wrapping.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        errors.append(f"{p.__name__} init failed: {e}")
                        continue
                else:
                    p_inst = p
                try:
                    return await p_inst.ask_async(query, **kwargs)
                except Exception as e:
                    errors.append(f"{p_inst.__class__.__name__}: {e}")
                    logger.warning("Provider fallback failed for %s: %s", p_inst.__class__.__name__, e)
            from .exceptions import ProviderError
            raise ProviderError(f"All fallback providers failed: {errors}")

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        output_type = kwargs.get('output_type')
        retry = int(kwargs.get('retry', final_config.extra.get('retry', 0)) or 0)
        response_model = kwargs.get('response_model')

        response = await self._execute_with_retry_async(
            self._send_request_async, messages, final_config, output_type, retry
        )
        if response_model:
            response.response_model = response_model
        return response

    async def ask_stream_async(self, query: str, **kwargs) -> AsyncIterator[str]:
        """
        Async streaming text generation. Yields text chunks.
        """
        providers = kwargs.pop("providers", None) or kwargs.pop("fallback", None)
        if providers:
            if not isinstance(providers, (list, tuple)):
                providers = [providers]
            errors = []
            for p in providers:
                if isinstance(p, type):
                    try:
                        p_inst = p()
                    except Exception as e:
                        errors.append(f"{p.__name__} init failed: {e}")
                        continue
                else:
                    p_inst = p
                try:
                    async for chunk in await p_inst.ask_stream_async(query, **kwargs):
                        yield chunk
                    return
                except Exception as e:
                    errors.append(f"{p_inst.__class__.__name__}: {e}")
                    logger.warning("Provider fallback failed for %s: %s", p_inst.__class__.__name__, e)
            from .exceptions import ProviderError
            raise ProviderError(f"All fallback providers failed: {errors}")

        final_config = self._build_final_config(kwargs)
        messages = self._prepare_messages(query, final_config)
        async for chunk in self._send_request_stream_async(messages, final_config):
            yield chunk

    # ─── Config Helpers ─────────────────────────────────────

    def _build_final_config(self, kwargs: Dict[str, Any]) -> AdvancedConfig:
        """Build final config by merging global config with per-request kwargs."""
        request_config = AdvancedConfig(**kwargs)
        final_config = self.config.merge(request_config)

        # Ensure timeout has a default
        timeout = kwargs.get('timeout', final_config.extra.get('timeout', 30))
        final_config.extra['timeout'] = float(timeout) if timeout is not None else 30.0

        return final_config

    def _prepare_messages(self, query: str, config: AdvancedConfig) -> List[Dict[str, str]]:
        """Build the messages list from query, persona, and config."""
        messages = []

        system_msg = config.system_message or self.persona or ""

        # Smart capability: if json=True or response_model is specified
        response_model = config.extra.get('response_model')
        if response_model:
            if hasattr(response_model, "model_json_schema"):
                schema = response_model.model_json_schema()
            elif hasattr(response_model, "schema"):
                schema = response_model.schema()
            else:
                schema = None

            if schema:
                import json
                schema_str = json.dumps(schema)
                json_instruction = (
                    f"You must respond with valid JSON matching the following JSON schema:\n"
                    f"{schema_str}\n"
                    f"Do not include any markdown markup, explanation, or HTML tags."
                )
            else:
                json_instruction = "You must respond with valid JSON only."

            system_msg = f"{system_msg}\n{json_instruction}".strip()
            config.extra['json'] = True

        elif config.extra.get('json'):
            json_instruction = "You must respond with valid JSON only, without any markdown formatting or tags."
            system_msg = f"{system_msg}\n{json_instruction}".strip()

        if system_msg:
            messages.append({"role": "system", "content": system_msg})

        messages.append({"role": "user", "content": query})
        return messages

    # ─── Retry Logic ────────────────────────────────────────

    def _execute_with_retry(self, func, messages, config, output_type, retry):
        """Execute a sync function with exponential backoff + jitter."""
        attempts = 0
        last_error = None

        while attempts <= retry:
            try:
                response = func(messages, config, output_type)
                return response
            except Exception as e:
                last_error = e
                if self._is_retryable_error(e) and attempts < retry:
                    attempts += 1
                    delay = min(2 ** attempts + random.uniform(0, 1), 30)
                    logger.warning(
                        "Transient error (%s). Retrying in %.1fs... (%d/%d)",
                        e.__class__.__name__, delay, attempts, retry
                    )
                    time.sleep(delay)
                else:
                    raise

        from .exceptions import AskAINetworkError
        raise AskAINetworkError(f"Request failed after {retry} retries. Last error: {last_error}")

    async def _execute_with_retry_async(self, func, messages, config, output_type, retry):
        """Execute an async function with exponential backoff + jitter."""
        attempts = 0
        last_error = None

        while attempts <= retry:
            try:
                response = await func(messages, config, output_type)
                return response
            except Exception as e:
                last_error = e
                if self._is_retryable_error(e) and attempts < retry:
                    attempts += 1
                    delay = min(2 ** attempts + random.uniform(0, 1), 30)
                    logger.warning(
                        "Transient error (%s). Retrying in %.1fs... (%d/%d)",
                        e.__class__.__name__, delay, attempts, retry
                    )
                    await asyncio.sleep(delay)
                else:
                    raise

        from .exceptions import AskAINetworkError
        raise AskAINetworkError(f"Request failed after {retry} retries. Last error: {last_error}")

    def _is_retryable_error(self, e: Exception) -> bool:
        """Dynamically detect rate limits and network timeouts across different provider SDKs."""
        from .exceptions import AskAINetworkError, AskAIRateLimitError
        if isinstance(e, (AskAINetworkError, AskAIRateLimitError)):
            return True

        err_str = str(e).lower()
        err_cls = e.__class__.__name__.lower()

        retryable_indicators = ("ratelimit", "rate_limit", "429", "timeout", "connection", "connecterror")
        return any(indicator in err_cls or indicator in err_str for indicator in retryable_indicators)

    # ─── Abstract Methods (Subclasses Must Implement) ──────

    def _send_request(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        """Sync request — subclasses must implement."""
        raise NotImplementedError

    async def _send_request_async(self, messages: List[Dict[str, str]], config: AdvancedConfig, output_type: str = None) -> Response:
        """Async request — subclasses should override for native async."""
        # Default fallback: run sync in thread pool
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._send_request, messages, config, output_type)

    def _send_request_stream(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> Iterator[str]:
        """Sync streaming — subclasses should override."""
        from .exceptions import StreamNotSupportedError
        raise StreamNotSupportedError(f"{self.__class__.__name__} does not support streaming.")

    async def _send_request_stream_async(self, messages: List[Dict[str, str]], config: AdvancedConfig) -> AsyncIterator[str]:
        """Async streaming — subclasses should override for native async."""
        # Default fallback: wrap sync stream
        loop = asyncio.get_running_loop()
        for chunk in await loop.run_in_executor(None, lambda: list(self._send_request_stream(messages, config))):
            yield chunk

    # ─── Tool Definitions for Smart Intent ─────────────────

    def _get_media_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": (
                        "Generate an image based on a prompt. Use this when the user asks to draw, create, or show an image."
                    ),
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
                    "description": (
                        "Generate audio speech from text. Use this when the user asks to say something, speak, or read aloud."
                    ),
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
