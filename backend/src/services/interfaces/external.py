"""
External Service Interface
Standardized interface for third-party service integrations
"""
from abc import abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .base import BaseService, ServiceConfig


class ExternalServiceType(str, Enum):
    """Types of external services"""
    WEATHER = "weather"
    MAPS = "maps"
    PLACES = "places"
    SEARCH = "search"
    BOOKING = "booking"
    TRANSLATION = "translation"
    CURRENCY = "currency"


class RequestMethod(str, Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class ExternalRequest:
    """External service request"""
    url: str
    method: RequestMethod = RequestMethod.GET
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.params is None:
            self.params = {}


@dataclass
class ExternalResponse:
    """External service response"""
    status_code: int
    data: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    response_time_ms: Optional[float] = None
    
    @property
    def is_success(self) -> bool:
        """Check if response was successful"""
        return 200 <= self.status_code < 300 and self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_code": self.status_code,
            "data": self.data,
            "text": self.text,
            "error": self.error,
            "request_id": self.request_id,
            "response_time_ms": self.response_time_ms,
            "success": self.is_success
        }


class ExternalServiceInterface(BaseService):
    """Interface for external services"""
    
    @property
    @abstractmethod
    def service_type(self) -> ExternalServiceType:
        """Get the service type"""
        pass
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Get the service name"""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Get the base URL for the service"""
        pass
    
    @property
    @abstractmethod
    def api_key_required(self) -> bool:
        """Check if API key is required"""
        pass
    
    @abstractmethod
    async def make_request(self, request: ExternalRequest) -> ExternalResponse:
        """Make a request to the external service"""
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate the API key"""
        pass
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "service_type": self.service_type.value,
            "service_name": self.service_name,
            "base_url": self.base_url,
            "api_key_required": self.api_key_required,
            "health_status": await self.get_health_status()
        }
    
    def build_request(
        self,
        endpoint: str,
        method: RequestMethod = RequestMethod.GET,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> ExternalRequest:
        """Build a request for this service"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Add default headers
        default_headers = self._get_default_headers()
        if headers:
            default_headers.update(headers)
        
        return ExternalRequest(
            url=url,
            method=method,
            headers=default_headers,
            params=params or {},
            data=data,
            timeout=self.config.timeout_seconds
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""
        return {
            "User-Agent": "TripCraft-AI/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }


class WeatherServiceInterface(ExternalServiceInterface):
    """Interface for weather services"""
    
    @property
    def service_type(self) -> ExternalServiceType:
        return ExternalServiceType.WEATHER
    
    @abstractmethod
    async def get_current_weather(
        self,
        location: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get current weather for location"""
        pass
    
    @abstractmethod
    async def get_weather_forecast(
        self,
        location: str,
        days: int = 5,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get weather forecast for location"""
        pass
    
    @abstractmethod
    async def get_weather_for_dates(
        self,
        location: str,
        start_date: str,
        end_date: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get weather for specific date range"""
        pass


class MapsServiceInterface(ExternalServiceInterface):
    """Interface for maps services"""
    
    @property
    def service_type(self) -> ExternalServiceType:
        return ExternalServiceType.MAPS
    
    @abstractmethod
    async def geocode_address(self, address: str) -> Dict[str, Any]:
        """Convert address to coordinates"""
        pass
    
    @abstractmethod
    async def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """Convert coordinates to address"""
        pass
    
    @abstractmethod
    async def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """Get directions between two points"""
        pass
    
    @abstractmethod
    async def get_distance_matrix(
        self,
        origins: List[str],
        destinations: List[str],
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """Get distance matrix for multiple points"""
        pass


class PlacesServiceInterface(ExternalServiceInterface):
    """Interface for places services"""
    
    @property
    def service_type(self) -> ExternalServiceType:
        return ExternalServiceType.PLACES
    
    @abstractmethod
    async def search_places(
        self,
        query: str,
        location: Optional[str] = None,
        radius: Optional[int] = None,
        place_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for places"""
        pass
    
    @abstractmethod
    async def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get detailed information about a place"""
        pass
    
    @abstractmethod
    async def get_nearby_places(
        self,
        lat: float,
        lng: float,
        radius: int = 1000,
        place_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get places near coordinates"""
        pass
    
    @abstractmethod
    async def get_place_photos(self, place_id: str) -> List[str]:
        """Get photos for a place"""
        pass


class SearchServiceInterface(ExternalServiceInterface):
    """Interface for search services (like Perplexity)"""
    
    @property
    def service_type(self) -> ExternalServiceType:
        return ExternalServiceType.SEARCH
    
    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_type: str = "web"
    ) -> Dict[str, Any]:
        """Perform a search query"""
        pass
    
    @abstractmethod
    async def search_with_context(
        self,
        query: str,
        context: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Search with additional context"""
        pass


class BookingServiceInterface(ExternalServiceInterface):
    """Interface for booking services"""
    
    @property
    def service_type(self) -> ExternalServiceType:
        return ExternalServiceType.BOOKING
    
    @abstractmethod
    async def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        guests: int = 1
    ) -> Dict[str, Any]:
        """Search for hotels"""
        pass
    
    @abstractmethod
    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1
    ) -> Dict[str, Any]:
        """Search for flights"""
        pass
    
    @abstractmethod
    async def get_booking_url(
        self,
        booking_type: str,
        booking_id: str,
        **params
    ) -> str:
        """Get booking URL for external booking"""
        pass
