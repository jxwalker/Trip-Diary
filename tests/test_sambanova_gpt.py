import os
import pytest
from src.gpt_providers.sambanova_gpt import SambanovaGPT

@pytest.fixture
def sambanova_gpt():
    api_key = os.getenv('SAMBANOVA_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the SAMBANOVA_API_KEY environment variable.")
    return SambanovaGPT(api_key=api_key)

def test_sambanova_gpt_generate_text(sambanova_gpt):
    prompt = "What is the capital of France?"
    response = sambanova_gpt.generate_text(prompt)
    assert "Paris" in response