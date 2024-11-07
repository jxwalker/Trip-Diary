import os
from openai import OpenAI
from src.gpt_interfaces.gpt_interface import GPTInterface

class OpenAIGPT(GPTInterface):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=api_key)

    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        system_content = system_prompt if system_prompt else "You are a helpful assistant."
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo"
        )
        return response.choices[0].message.content.strip()