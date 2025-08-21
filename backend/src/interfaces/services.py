"""
Service interfaces for improved testability and dependency injection
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path


class PDFProcessorInterface(ABC):
    """Interface for PDF processing services"""

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF file"""
        pass

    @abstractmethod
    def validate_pdf(self, file_path: str) -> bool:
        """Validate if file is a readable PDF"""
        pass


class LLMExtractorInterface(ABC):
    """Interface for LLM-based data extraction services"""

    @abstractmethod
    async def extract_travel_data(self, text: str) -> Dict[str, Any]:
        """Extract structured travel data from text"""
        pass


class GuideGeneratorInterface(ABC):
    """Interface for travel guide generation services"""

    @abstractmethod
    async def generate_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        preferences: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate travel guide for destination"""
        pass
