import os
from anthropic import Anthropic
from src.gpt_interfaces.gpt_interface import GPTInterface
import json

class XAIGPT(GPTInterface):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('XAI_API_KEY')
            if not api_key:
                raise ValueError("API key not found. Please set the XAI_API_KEY environment variable.")
        self.client = Anthropic(
            api_key=api_key,
            base_url="https://api.x.ai"
        )

    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        try:
            # Let PDFProcessor handle the JSON validation and cleaning
            # Just focus on getting a clean response from the API
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "user",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.messages.create(
                model="grok-beta",
                max_tokens=2048,
                messages=messages
            )
            
            if not hasattr(response, 'content') or not response.content:
                raise Exception("Empty response from API")
                
            return response.content[0].text.strip()
            
        except Exception as e:
            raise Exception(f"XAI API error: {str(e)}")