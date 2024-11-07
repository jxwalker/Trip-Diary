import os
from dotenv import load_dotenv
import pytest
from src.gpt_providers.xai_gpt import XAIGPT

   # Load environment variables from .env file
load_dotenv()

@pytest.fixture
def xai_gpt():
   api_key = os.getenv('XAI_API_KEY')
   if not api_key:
       raise ValueError("API key not found. Please set the XAI_API_KEY environment variable.")
   return XAIGPT(api_key=api_key)

def test_xai_gpt_generate_text(xai_gpt):
   prompt = "What is the capital of France?"
   response = xai_gpt.generate_text(prompt)
   assert "Paris" in response