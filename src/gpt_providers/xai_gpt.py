import os
from anthropic import Anthropic
from src.gpt_interfaces.gpt_interface import GPTInterface
import json
from typing import Dict, Any

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

    def generate_text(self, prompt: str, system: str | None = None) -> Dict[str, Any]:
        try:
            messages = []
            
            if system:
                messages.append({
                    "role": "system",
                    "content": system
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
                
            # Parse the response into structured data
            content = response.content[0].text.strip()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise Exception("Failed to parse response as JSON")
            
        except Exception as e:
            logger.error(f"XAI API error: {str(e)}")
            return {
                "flights": [],
                "hotels": [],
                "passengers": []
            }