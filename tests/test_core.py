import os
from ask_ai import OpenAI, Groq, Google, OpenRouter, Azure, Anthropic, AdvancedConfig

def test_advanced_config_defaults():
    config = AdvancedConfig()
    assert config.temperature is None
    assert config.max_tokens is None
    assert config.system_message is None

def test_advanced_config_aliases():
    config = AdvancedConfig(prompt="System Prompt")
    assert config.system_message == "System Prompt"
    
    config2 = AdvancedConfig(system="System Prompt 2")
    assert config2.system_message == "System Prompt 2"

def test_provider_instantiation():
    # These should succeed with a fake key because clients are lazy-loaded or just stored
    # We set env var to None to ensure it uses the passed key
    os.environ.pop("OPENAI_API_KEY", None)
        
    ai = OpenAI(api_key="sk-fake-key-for-testing")
    assert ai.api_key == "sk-fake-key-for-testing"
    assert ai.model == "gpt-4o"  # Default model check

def test_azure_instantiation():
    az = Azure(
        api_key="fake", 
        endpoint="https://example.com", 
        api_version="2023-01-01", 
        deployment_name="dep"
    )
    assert az.api_key == "fake"
    assert az.endpoint == "https://example.com"
