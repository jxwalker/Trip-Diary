import os
import openai
from src.gpt_interfaces.gpt_interface import GPTInterface

class SambanovaGPT(GPTInterface):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('SAMBANOVA_API_KEY')
            if not api_key:
                raise ValueError("API key not found. Please set the SAMBANOVA_API_KEY environment variable.")
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.sambanova.ai/v1"
        )

    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        system_content = system_prompt if system_prompt else "You are a helpful assistant"
        response = self.client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1
        )
        return response.choices[0].message.content.strip()