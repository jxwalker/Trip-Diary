"""
Base service interface and configuration
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime
import logging

T = TypeVar('T')


@dataclass
class ServiceConfig:
    """Base configuration for services"""
    enabled: bool = True
    timeout_seconds: int = 60
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    
    def __post_init__(self):
        """Validate configuration"""
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be non-negative")
        if self.retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be non-negative")


class BaseService(ABC, Generic[T]):
    """Base class for all services"""
    
    def __init__(self, config: ServiceConfig, 
                 logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._initialized = False
        self._last_health_check = None
        self._health_status = "unknown"
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup service resources"""
        pass
    
    async def ensure_initialized(self) -> None:
        """Ensure service is initialized"""
        if not self._initialized:
            await self.initialize()
            self._initialized = True
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get cached health status or perform new check"""
        now = datetime.now()
        
        # Check if we need to refresh health status
        if (self._last_health_check is None or 
            (now - self._last_health_check).seconds > 60):
            
            try:
                health_data = await self.health_check()
                self._health_status = health_data.get("status", "unknown")
                self._last_health_check = now
                return health_data
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                self._health_status = "unhealthy"
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": now.isoformat()
                }
        
        return {
            "status": self._health_status,
            "last_check": (self._last_health_check.isoformat() 
                          if self._last_health_check else None)
        }
    
    def is_enabled(self) -> bool:
        """Check if service is enabled"""
        return self.config.enabled
    
    def is_healthy(self) -> bool:
        """Check if service is healthy"""
        return self._health_status == "healthy"
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()


class ServiceRegistry:
    """Registry for managing service instances"""
    
    def __init__(self):
        self._services: Dict[str, BaseService] = {}
        self._configs: Dict[str, ServiceConfig] = {}
    
    def register(self, name: str, service: BaseService, 
                 config: Optional[ServiceConfig] = None):
        """Register a service"""
        self._services[name] = service
        if config:
            self._configs[name] = config
    
    def get(self, name: str) -> Optional[BaseService]:
        """Get a service by name"""
        return self._services.get(name)
    
    def get_config(self, name: str) -> Optional[ServiceConfig]:
        """Get service configuration"""
        return self._configs.get(name)
    
    def list_services(self) -> Dict[str, str]:
        """List all registered services"""
        return {name: service.__class__.__name__ 
                for name, service in self._services.items()}
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Health check all services"""
        results = {}
        for name, service in self._services.items():
            try:
                results[name] = await service.get_health_status()
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        return results
    
    async def initialize_all(self) -> Dict[str, bool]:
        """Initialize all services"""
        results = {}
        for name, service in self._services.items():
            try:
                await service.ensure_initialized()
                results[name] = True
            except Exception as e:
                logging.error(f"Failed to initialize service {name}: {e}")
                results[name] = False
        return results
    
    async def cleanup_all(self) -> None:
        """Cleanup all services"""
        for name, service in self._services.items():
            try:
                await service.cleanup()
            except Exception as e:
                logging.error(f"Failed to cleanup service {name}: {e}")


# Global service registry instance
service_registry = ServiceRegistry()
