import os
import pytest
from src.gpt_providers.openai_gpt import OpenAIGPT

@pytest.fixture
def openai_gpt():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
    return OpenAIGPT(api_key=api_key)

def test_openai_gpt_generate_text(openai_gpt):
    prompt = "What is the capital of France?"
    response = openai_gpt.generate_text(prompt)
    assert "Paris" in response