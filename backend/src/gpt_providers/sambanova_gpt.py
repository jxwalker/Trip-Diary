import os
import openai
import json
from src.gpt_interfaces.gpt_interface import GPTInterface
from typing import Dict, Any

class SambanovaGPT(GPTInterface):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('SAMBANOVA_API_KEY')
            if not api_key:
                raise ValueError(
                    "API key not found. Please set the SAMBANOVA_API_KEY "
                    "environment variable."
                )
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.sambanova.ai/v1"
        )

    def generate_text(
        self, prompt: str, system: str | None = None
    ) -> Dict[str, Any]:
        system_content = (
            f"{system}\n\n"
            "IMPORTANT: You must respond with ONLY a valid JSON object. "
            "Do not include any other text, markdown formatting, "
            "or explanations."
        ) if system else "You are a helpful assistant"

        try:
            response = self.client.chat.completions.create(
                model='Meta-Llama-3.1-8B-Instruct',
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                top_p=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract and validate JSON
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in response: {content}")
                
            # Return empty structure on failure
            return {
                "flights": [],
                "hotels": [],
                "passengers": []
            }
            
        except Exception as e:
            logger.error(f"SambaNova API error: {str(e)}")
            return {
                "flights": [],
                "hotels": [],
                "passengers": []
            }
