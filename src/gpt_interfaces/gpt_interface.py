from abc import ABC, abstractmethod

class GPTInterface(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text based on the given prompt and optional system prompt."""
        pass