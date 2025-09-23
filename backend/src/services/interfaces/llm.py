"""
LLM Service Interface
Standardized interface for all language model services
"""
from abc import abstractmethod
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

from .base import BaseService, ServiceConfig


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    PERPLEXITY = "perplexity"
    SAMBANOVA = "sambanova"
    XAI = "xai"


class LLMCapability(str, Enum):
    """LLM capabilities"""
    TEXT_GENERATION = "text_generation"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    EMBEDDINGS = "embeddings"


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: LLMProvider
    model: str
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """Check if response was successful"""
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "provider": self.provider.value,
            "model": self.model,
            "usage": self.usage,
            "metadata": self.metadata,
            "error": self.error,
            "success": self.is_success
        }


@dataclass
class LLMRequest:
    """Standardized LLM request"""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    images: Optional[List[str]] = None  # Base64 encoded images
    functions: Optional[List[Dict[str, Any]]] = None
    stream: bool = False
    metadata: Optional[Dict[str, Any]] = None


class LLMServiceInterface(BaseService):
    """Interface for LLM services"""
    
    @property
    @abstractmethod
    def provider(self) -> LLMProvider:
        """Get the LLM provider"""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[LLMCapability]:
        """Get supported capabilities"""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """Get available models"""
        pass
    
    @abstractmethod
    async def generate_response(
        self,
        request: Union[LLMRequest, str],
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_streaming_response(
        self,
        request: Union[LLMRequest, str],
        callback: Callable[[str], Awaitable[None]],
        **kwargs
    ) -> LLMResponse:
        """Generate a streaming response from the LLM"""
        pass
    
    async def extract_travel_info(
        self,
        text: str,
        extraction_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Extract travel information from text"""
        prompt = self._build_extraction_prompt(text, extraction_type)
        request = LLMRequest(prompt=prompt)
        response = await self.generate_response(request)
        
        if not response.is_success:
            raise Exception(f"LLM extraction failed: {response.error}")
        
        return self._parse_extraction_response(response.content)
    
    async def generate_itinerary(
        self,
        extracted_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate travel itinerary from extracted data"""
        prompt = self._build_itinerary_prompt(extracted_data, preferences)
        request = LLMRequest(prompt=prompt)
        response = await self.generate_response(request)
        
        if not response.is_success:
            raise Exception(f"Itinerary generation failed: {response.error}")
        
        return self._parse_itinerary_response(response.content)
    
    async def generate_travel_guide(
        self,
        destination: str,
        preferences: Dict[str, Any],
        progress_callback: Optional[
            Callable[[int, str], Awaitable[None]]
        ] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive travel guide"""
        if progress_callback:
            await progress_callback(10, "Starting guide generation...")
        
        prompt = self._build_guide_prompt(destination, preferences)
        request = LLMRequest(prompt=prompt)
        response = await self.generate_response(request)
        
        if progress_callback:
            await progress_callback(90, "Processing guide content...")
        
        if not response.is_success:
            raise Exception(f"Guide generation failed: {response.error}")
        
        guide = self._parse_guide_response(response.content)
        
        if progress_callback:
            await progress_callback(100, "Guide generation complete")
        
        return guide
    
    def supports_capability(self, capability: LLMCapability) -> bool:
        """Check if service supports a capability"""
        return capability in self.capabilities
    
    def supports_vision(self) -> bool:
        """Check if service supports vision/image processing"""
        return self.supports_capability(LLMCapability.VISION)
    
    def supports_streaming(self) -> bool:
        """Check if service supports streaming responses"""
        return self.supports_capability(LLMCapability.STREAMING)
    
    def _build_extraction_prompt(self, text: str, extraction_type: str) -> str:
        """Build prompt for travel information extraction"""
        base_prompt = f"""
        Extract travel information from the following text and return as JSON:
        
        Text: {text}
        
        Extract:
        - flights (flight_number, airline, departure/arrival airports and 
          times)
        - hotels (name, location, check-in/out dates, confirmation codes)
        - passengers (names, contact info)
        - activities (if mentioned)
        
        Return valid JSON only.
        """
        return base_prompt.strip()
    
    def _build_itinerary_prompt(
        self,
        extracted_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for itinerary generation"""
        prompt = f"""
        Create a detailed travel itinerary based on this information:
        
        Extracted Data: {extracted_data}
        """
        
        if preferences:
            prompt += f"\nUser Preferences: {preferences}"
        
        prompt += """
        
        Generate a comprehensive itinerary with:
        - Trip summary (destination, dates, duration)
        - Daily schedules
        - Transportation details
        - Accommodation information
        - Recommended activities
        
        Return as valid JSON.
        """
        
        return prompt.strip()
    
    def _build_guide_prompt(
        self, destination: str, preferences: Dict[str, Any]
    ) -> str:
        """Build prompt for travel guide generation"""
        return f"""
        Create a comprehensive travel guide for {destination} based on these 
        preferences:
        
        Preferences: {preferences}
        
        Include:
        - Local attractions and activities
        - Restaurant recommendations
        - Cultural insights
        - Practical travel tips
        - Transportation options
        - Safety information
        
        Return as structured JSON with clear sections.
        """
    
    def _parse_extraction_response(self, content: str) -> Dict[str, Any]:
        """Parse extraction response from LLM"""
        try:
            import json
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Failed to parse extraction response"}
    
    def _parse_itinerary_response(self, content: str) -> Dict[str, Any]:
        """Parse itinerary response from LLM"""
        return self._parse_extraction_response(content)
    
    def _parse_guide_response(self, content: str) -> Dict[str, Any]:
        """Parse guide response from LLM"""
        return self._parse_extraction_response(content)
