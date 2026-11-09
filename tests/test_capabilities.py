import pytest

from ask_ai import AdvancedConfig, Anthropic, Capabilities, Groq, OpenAI, OpenRouter
from ask_ai.base import BaseProvider
from ask_ai.exceptions import MediaTypeNotSupportedError
from ask_ai.providers.google_provider import GoogleProvider


def test_provider_capabilities_are_explicit():
    assert OpenAI.capabilities(OpenAI.__new__(OpenAI)).image_generation is True
    assert Anthropic.capabilities(Anthropic.__new__(Anthropic)).vision is False
    assert OpenAI.capabilities(OpenAI.__new__(OpenAI)).vision is False
    assert Groq.capabilities(Groq.__new__(Groq)).audio_generation is False
    assert OpenRouter.capabilities(OpenRouter.__new__(OpenRouter)).image_generation is True


def test_custom_provider_has_conservative_capabilities():
    provider = object.__new__(BaseProvider)
    capabilities = provider.capabilities()
    assert capabilities == Capabilities()
    assert capabilities.to_dict()["text"] is True


def test_google_structured_capability_is_true():
    assert GoogleProvider.capabilities(object.__new__(GoogleProvider)).structured_output is True


def test_unsupported_image_and_output_types_fail_before_provider_request():
    provider = object.__new__(BaseProvider)
    provider.config = AdvancedConfig()
    provider.strict_options = False
    provider.model = "test"
    provider.persona = None
    provider._middleware = []
    provider._retry_count_var = None

    with pytest.raises(MediaTypeNotSupportedError, match="Image input"):
        provider._build_final_config({"image": b"image"})
    with pytest.raises(ValueError, match="Unsupported output_type"):
        provider._build_final_config({"output_type": "video"})
    with pytest.raises(MediaTypeNotSupportedError, match="image generation"):
        provider._build_final_config({"output_type": "image"})
