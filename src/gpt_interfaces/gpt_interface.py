from abc import ABC, abstractmethod
from typing import Dict, Any

class GPTInterface(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system: str | None = None) -> Dict[str, Any]:
        """Generate structured output from prompt."""
        pass