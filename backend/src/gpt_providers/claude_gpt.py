import os
from anthropic import Anthropic
from src.gpt_interfaces.gpt_interface import GPTInterface

class ClaudeGPT(GPTInterface):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
        self.client = Anthropic(api_key=api_key)

    def generate_text(self, prompt: str, system: str | None = None) -> str:
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
        
        message = self.client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            max_tokens=4000,
            temperature=0,
            messages=messages
        )
        return message.content
