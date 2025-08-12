import os
import pytest
from dotenv import load_dotenv
from src.gpt_providers.gpt_selector import GPTSelector
from src.gpt_providers.openai_gpt import OpenAIGPT
from src.gpt_providers.claude_gpt import ClaudeGPT
from src.gpt_providers.xai_gpt import XAIGPT
from src.gpt_providers.sambanova_gpt import SambanovaGPT

load_dotenv()

@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables."""
    env_vars = {
        'OPENAI_API_KEY': 'mock-openai-key',
        'ANTHROPIC_API_KEY': 'mock-claude-key',
        'XAI_API_KEY': 'mock-xai-key',
        'SAMBANOVA_API_KEY': 'mock-sambanova-key'
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

@pytest.fixture
def gpt_selector(mock_env):
    """Create a GPT selector with mock environment variables."""
    return GPTSelector()

def test_get_provider_openai(gpt_selector):
    """Test getting OpenAI provider."""
    provider = gpt_selector.get_provider("openai")
    assert isinstance(provider, OpenAIGPT)

def test_get_provider_claude(gpt_selector):
    """Test getting Claude provider."""
    provider = gpt_selector.get_provider("claude")
    assert isinstance(provider, ClaudeGPT)

def test_get_provider_xai(gpt_selector):
    """Test getting XAI provider."""
    provider = gpt_selector.get_provider("xai")
    assert isinstance(provider, XAIGPT)

def test_get_provider_sambanova(gpt_selector):
    """Test getting Sambanova provider."""
    provider = gpt_selector.get_provider("sambanova")
    assert isinstance(provider, SambanovaGPT)

def test_get_provider_invalid(gpt_selector):
    """Test error handling for invalid provider."""
    with pytest.raises(ValueError) as exc_info:
        gpt_selector.get_provider("invalid_provider")
    assert "Unknown provider: invalid_provider" in str(exc_info.value)

def test_get_provider_missing_api_key(monkeypatch):
    """Test error handling for missing API key."""
    # Create a new selector without mock environment
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    selector = GPTSelector()
    
    with pytest.raises(ValueError) as exc_info:
        selector.get_provider("openai")
    assert "API key not found for provider: openai" in str(exc_info.value)

@pytest.mark.skip(reason="Requires valid API key")
def test_provider_text_generation(gpt_selector):
    """Test text generation with selected provider."""
    provider = gpt_selector.get_provider("openai")
    response = provider.generate_text("What is the capital of France?")
    assert isinstance(response, str)
    assert len(response) > 0

def test_get_default_provider(gpt_selector):
    """Test getting default provider (should be OpenAI)."""
    provider = gpt_selector.get_provider()  # No argument should default to OpenAI
    assert isinstance(provider, OpenAIGPT)
