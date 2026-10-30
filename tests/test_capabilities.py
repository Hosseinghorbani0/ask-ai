from ask_ai import Anthropic, Capabilities, Groq, OpenAI, OpenRouter


def test_provider_capabilities_are_explicit():
    assert OpenAI.capabilities(OpenAI.__new__(OpenAI)).image_generation is True
    assert Anthropic.capabilities(Anthropic.__new__(Anthropic)).vision is True
    assert Groq.capabilities(Groq.__new__(Groq)).audio_generation is False
    assert OpenRouter.capabilities(OpenRouter.__new__(OpenRouter)).image_generation is False


def test_custom_provider_has_conservative_capabilities():
    from ask_ai.base import BaseProvider

    provider = object.__new__(BaseProvider)
    capabilities = provider.capabilities()
    assert capabilities == Capabilities()
    assert capabilities.to_dict()["text"] is True
