import pytest
from src.gpt_interfaces.gpt_interface import GPTInterface

class TestGPT(GPTInterface):
    def generate_text(self, prompt: str) -> str:
        return "Test response"

def test_gpt_interface():
    test_gpt = TestGPT()
    response = test_gpt.generate_text("Hello, world!")
    assert response == "Test response"