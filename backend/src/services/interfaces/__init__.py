"""
Service interfaces for TripCraft AI
Abstract base classes and protocols for all services
"""

from .base import BaseService, ServiceConfig, service_registry
from .llm import (
    LLMServiceInterface,
    LLMResponse,
    LLMRequest,
    LLMProvider,
    LLMCapability
)
from .storage import (
    StorageServiceInterface,
    StorageResult,
    QueryFilter,
    QueryOptions,
    StorageType,
    QueryOperator
)
from .external import (
    ExternalServiceInterface,
    ExternalRequest,
    ExternalResponse,
    WeatherServiceInterface,
    MapsServiceInterface,
    PlacesServiceInterface,
    SearchServiceInterface,
    BookingServiceInterface,
    ExternalServiceType,
    RequestMethod
)
from .processing import (
    ProcessingServiceInterface,
    PDFProcessorInterface,
    ImageProcessorInterface,
    MultimodalProcessorInterface,
    TextProcessorInterface,
    ProcessingRequest,
    ProcessingResult,
    ProcessingType,
    FileType
)

__all__ = [
    # Base
    'BaseService',
    'ServiceConfig',
    'service_registry',

    # LLM
    'LLMServiceInterface',
    'LLMResponse',
    'LLMRequest',
    'LLMProvider',
    'LLMCapability',

    # Storage
    'StorageServiceInterface',
    'StorageResult',
    'QueryFilter',
    'QueryOptions',
    'StorageType',
    'QueryOperator',

    # External
    'ExternalServiceInterface',
    'ExternalRequest',
    'ExternalResponse',
    'WeatherServiceInterface',
    'MapsServiceInterface',
    'PlacesServiceInterface',
    'SearchServiceInterface',
    'BookingServiceInterface',
    'ExternalServiceType',
    'RequestMethod',

    # Processing
    'ProcessingServiceInterface',
    'PDFProcessorInterface',
    'ImageProcessorInterface',
    'MultimodalProcessorInterface',
    'TextProcessorInterface',
    'ProcessingRequest',
    'ProcessingResult',
    'ProcessingType',
    'FileType',
]
