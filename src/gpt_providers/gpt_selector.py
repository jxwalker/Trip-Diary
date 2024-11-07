from typing import Dict
from src.gpt_providers.openai_gpt import OpenAIGPT
from src.gpt_providers.claude_gpt import ClaudeGPT
from src.gpt_providers.xai_gpt import XAIGPT
from src.gpt_providers.sambanova_gpt import SambanovaGPT
from src.gpt_interfaces.gpt_interface import GPTInterface
import os

class GPTSelector:
    def __init__(self):
        self.providers = {
            "openai": (OpenAIGPT, 'OPENAI_API_KEY'),
            "claude": (ClaudeGPT, 'ANTHROPIC_API_KEY'),
            "xai": (XAIGPT, 'XAI_API_KEY'),
            "sambanova": (SambanovaGPT, 'SAMBANOVA_API_KEY')
        }
        
    def get_provider(self, provider_name: str = "openai") -> GPTInterface:
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
            
        provider_class, env_key = self.providers[provider_name]
        api_key = os.getenv(env_key)
        
        if not api_key:
            raise ValueError(f"API key not found for provider: {provider_name}")
            
        return provider_class(api_key=api_key)
