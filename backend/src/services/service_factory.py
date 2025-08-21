"""
Service Factory
Centralized service creation and management
"""
import logging
from typing import Dict, Any, Optional, Type, TypeVar, Union
from enum import Enum

from .interfaces import (
    BaseService,
    ServiceConfig,
    service_registry,
    LLMServiceInterface,
    LLMProvider,
    StorageServiceInterface,
    ExternalServiceInterface,
    ProcessingServiceInterface,
    WeatherServiceInterface
)
from .enhanced_database_service import EnhancedDatabaseService
from .enhanced_llm_service import EnhancedLLMService
from .enhanced_weather_service import EnhancedWeatherService
from .enhanced_pdf_processor import EnhancedPDFProcessor
from ..core.exceptions import ConfigurationError, ServiceError
from ..config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseService)


class ServiceType(str, Enum):
    """Available service types"""
    STORAGE = "storage"
    LLM = "llm"
    WEATHER = "weather"
    PROCESSING = "processing"
    EXTERNAL = "external"


class ServiceFactory:
    """Factory for creating and managing services"""
    
    def __init__(self):
        self.settings = get_settings()
        self._service_configs: Dict[str, ServiceConfig] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the service factory"""
        if self._initialized:
            return
        
        try:
            # Load service configurations
            await self._load_service_configs()
            
            # Create and register core services
            await self._create_core_services()
            
            # Initialize all services
            await service_registry.initialize_all()
            
            self._initialized = True
            logger.info("Service factory initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize service factory: {e}")
            raise ConfigurationError(f"Service factory initialization failed: {e}")
    
    async def create_storage_service(
        self,
        service_name: str = "default",
        config: Optional[ServiceConfig] = None
    ) -> StorageServiceInterface:
        """Create a storage service"""
        try:
            if config is None:
                config = self._get_service_config("storage", service_name)
            
            # For now, we only have file-based storage
            # In the future, this could create different storage backends
            service = EnhancedDatabaseService(config)
            
            # Register the service
            service_registry.register(f"storage_{service_name}", service, config)
            
            return service
            
        except Exception as e:
            raise ServiceError(f"Failed to create storage service: {e}")
    
    async def create_llm_service(
        self,
        provider: Union[LLMProvider, str],
        service_name: Optional[str] = None,
        config: Optional[ServiceConfig] = None
    ) -> LLMServiceInterface:
        """Create an LLM service"""
        try:
            if isinstance(provider, str):
                provider = LLMProvider(provider)
            
            if service_name is None:
                service_name = provider.value
            
            if config is None:
                config = self._get_service_config("llm", service_name)
            
            # Check if provider is enabled
            if not self._is_provider_enabled(provider):
                raise ConfigurationError(f"Provider {provider} is not enabled")
            
            service = EnhancedLLMService(provider, config)
            
            # Register the service
            service_registry.register(f"llm_{service_name}", service, config)
            
            return service
            
        except Exception as e:
            raise ServiceError(f"Failed to create LLM service for {provider}: {e}")
    
    async def create_weather_service(
        self,
        service_name: str = "default",
        config: Optional[ServiceConfig] = None
    ) -> WeatherServiceInterface:
        """Create a weather service"""
        try:
            if config is None:
                config = self._get_service_config("weather", service_name)

            # Check if weather service is enabled
            if not self.settings.services.weather_enabled:
                raise ConfigurationError("Weather service is not enabled")

            service = EnhancedWeatherService(config)

            # Register the service
            service_registry.register(f"weather_{service_name}", service, config)

            return service

        except Exception as e:
            raise ServiceError(f"Failed to create weather service: {e}")

    async def create_processing_service(
        self,
        processing_type: str,
        service_name: str = "default",
        config: Optional[ServiceConfig] = None
    ) -> ProcessingServiceInterface:
        """Create a processing service"""
        try:
            if config is None:
                config = self._get_service_config("processing", service_name)

            if processing_type == "pdf":
                service = EnhancedPDFProcessor(config)
            else:
                raise ConfigurationError(f"Unsupported processing type: {processing_type}")

            # Register the service
            service_registry.register(f"processing_{processing_type}_{service_name}", service, config)

            return service

        except Exception as e:
            raise ServiceError(f"Failed to create processing service: {e}")

    async def create_external_service(
        self,
        service_type: str,
        service_name: str,
        config: Optional[ServiceConfig] = None
    ) -> ExternalServiceInterface:
        """Create an external service"""
        # This would be implemented based on specific external service needs
        raise NotImplementedError("External service creation not yet implemented")
    
    def get_service(self, service_name: str) -> Optional[BaseService]:
        """Get a service by name"""
        return service_registry.get(service_name)
    
    def get_storage_service(self, service_name: str = "default") -> Optional[StorageServiceInterface]:
        """Get a storage service"""
        service = service_registry.get(f"storage_{service_name}")
        if service and isinstance(service, StorageServiceInterface):
            return service
        return None
    
    def get_llm_service(self, provider: Union[LLMProvider, str]) -> Optional[LLMServiceInterface]:
        """Get an LLM service"""
        if isinstance(provider, LLMProvider):
            provider = provider.value

        service = service_registry.get(f"llm_{provider}")
        if service and isinstance(service, LLMServiceInterface):
            return service
        return None

    def get_weather_service(self, service_name: str = "default") -> Optional[WeatherServiceInterface]:
        """Get a weather service"""
        service = service_registry.get(f"weather_{service_name}")
        if service and isinstance(service, WeatherServiceInterface):
            return service
        return None

    def get_processing_service(self, processing_type: str, service_name: str = "default") -> Optional[ProcessingServiceInterface]:
        """Get a processing service"""
        service = service_registry.get(f"processing_{processing_type}_{service_name}")
        if service and isinstance(service, ProcessingServiceInterface):
            return service
        return None
    
    async def get_or_create_storage_service(
        self,
        service_name: str = "default"
    ) -> StorageServiceInterface:
        """Get existing storage service or create new one"""
        service = self.get_storage_service(service_name)
        if service:
            return service
        
        return await self.create_storage_service(service_name)
    
    async def get_or_create_llm_service(
        self,
        provider: Union[LLMProvider, str]
    ) -> LLMServiceInterface:
        """Get existing LLM service or create new one"""
        service = self.get_llm_service(provider)
        if service:
            return service

        return await self.create_llm_service(provider)

    async def get_or_create_weather_service(
        self,
        service_name: str = "default"
    ) -> WeatherServiceInterface:
        """Get existing weather service or create new one"""
        service = self.get_weather_service(service_name)
        if service:
            return service

        return await self.create_weather_service(service_name)

    async def get_or_create_processing_service(
        self,
        processing_type: str,
        service_name: str = "default"
    ) -> ProcessingServiceInterface:
        """Get existing processing service or create new one"""
        service = self.get_processing_service(processing_type, service_name)
        if service:
            return service

        return await self.create_processing_service(processing_type, service_name)
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Health check all services"""
        return await service_registry.health_check_all()
    
    async def cleanup_all(self) -> None:
        """Cleanup all services"""
        await service_registry.cleanup_all()
    
    def list_services(self) -> Dict[str, str]:
        """List all registered services"""
        return service_registry.list_services()
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service factory information"""
        return {
            "initialized": self._initialized,
            "total_services": len(service_registry.list_services()),
            "services": service_registry.list_services(),
            "enabled_providers": self._get_enabled_providers(),
            "service_configs": list(self._service_configs.keys())
        }
    
    # Private methods
    async def _load_service_configs(self) -> None:
        """Load service configurations"""
        # Storage service config
        self._service_configs["storage_default"] = ServiceConfig(
            enabled=True,
            timeout_seconds=30,
            cache_enabled=self.settings.database.cache_enabled,
            cache_ttl_seconds=self.settings.database.cache_ttl_seconds
        )
        
        # LLM service configs
        for provider in LLMProvider:
            if self._is_provider_enabled(provider):
                timeout = self._get_provider_timeout(provider)
                self._service_configs[f"llm_{provider.value}"] = ServiceConfig(
                    enabled=True,
                    timeout_seconds=timeout,
                    retry_attempts=self.settings.services.retry_max_attempts,
                    cache_enabled=True,
                    cache_ttl_seconds=300
                )
    
    async def _create_core_services(self) -> None:
        """Create core services"""
        # Create default storage service
        await self.create_storage_service("default")

        # Create enabled LLM services
        for provider in LLMProvider:
            if self._is_provider_enabled(provider):
                try:
                    await self.create_llm_service(provider)
                    logger.info(f"Created LLM service for {provider.value}")
                except Exception as e:
                    logger.warning(f"Failed to create LLM service for {provider.value}: {e}")

        # Create weather service if enabled
        if self.settings.services.weather_enabled:
            try:
                await self.create_weather_service("default")
                logger.info("Created weather service")
            except Exception as e:
                logger.warning(f"Failed to create weather service: {e}")

        # Create PDF processing service if enabled
        if self.settings.services.pdf_enabled:
            try:
                await self.create_processing_service("pdf", "default")
                logger.info("Created PDF processing service")
            except Exception as e:
                logger.warning(f"Failed to create PDF processing service: {e}")
    
    def _get_service_config(self, service_type: str, service_name: str) -> ServiceConfig:
        """Get service configuration"""
        config_key = f"{service_type}_{service_name}"
        return self._service_configs.get(config_key, ServiceConfig())
    
    def _is_provider_enabled(self, provider: LLMProvider) -> bool:
        """Check if LLM provider is enabled"""
        if provider == LLMProvider.OPENAI:
            return self.settings.services.openai_enabled and bool(self.settings.services.openai_api_key)
        elif provider == LLMProvider.ANTHROPIC:
            return self.settings.services.anthropic_enabled and bool(self.settings.services.anthropic_api_key)
        elif provider == LLMProvider.PERPLEXITY:
            return self.settings.services.perplexity_enabled and bool(self.settings.services.perplexity_api_key)
        else:
            return False
    
    def _get_provider_timeout(self, provider: LLMProvider) -> int:
        """Get timeout for LLM provider"""
        if provider == LLMProvider.OPENAI:
            return self.settings.services.openai_timeout
        elif provider == LLMProvider.ANTHROPIC:
            return self.settings.services.anthropic_timeout
        elif provider == LLMProvider.PERPLEXITY:
            return self.settings.services.perplexity_timeout
        else:
            return 60
    
    def _get_enabled_providers(self) -> Dict[str, bool]:
        """Get enabled providers"""
        return {
            provider.value: self._is_provider_enabled(provider)
            for provider in LLMProvider
        }


# Global service factory instance
service_factory = ServiceFactory()


# Convenience functions
async def get_storage_service(service_name: str = "default") -> StorageServiceInterface:
    """Get storage service"""
    if not service_factory._initialized:
        await service_factory.initialize()
    
    return await service_factory.get_or_create_storage_service(service_name)


async def get_llm_service(provider: Union[LLMProvider, str]) -> LLMServiceInterface:
    """Get LLM service"""
    if not service_factory._initialized:
        await service_factory.initialize()

    return await service_factory.get_or_create_llm_service(provider)


async def get_weather_service(service_name: str = "default") -> WeatherServiceInterface:
    """Get weather service"""
    if not service_factory._initialized:
        await service_factory.initialize()

    return await service_factory.get_or_create_weather_service(service_name)


async def get_processing_service(processing_type: str, service_name: str = "default") -> ProcessingServiceInterface:
    """Get processing service"""
    if not service_factory._initialized:
        await service_factory.initialize()

    return await service_factory.get_or_create_processing_service(processing_type, service_name)


async def initialize_services() -> None:
    """Initialize all services"""
    await service_factory.initialize()


async def cleanup_services() -> None:
    """Cleanup all services"""
    await service_factory.cleanup_all()


async def health_check_services() -> Dict[str, Dict[str, Any]]:
    """Health check all services"""
    return await service_factory.health_check_all()
