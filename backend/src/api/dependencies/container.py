"""
Dependency injection container for services
"""
import logging
from typing import Dict, Any, Optional
from functools import lru_cache

from ...services.pdf_processor import PDFProcessor
from ...services.llm_extractor import LLMExtractor
from ...services.enhanced_guide_service import EnhancedGuideService
from ...services.fast_guide_service import FastGuideService
from ...services.optimized_guide_service import OptimizedGuideService
from ...services.immediate_guide_generator import ImmediateGuideGenerator
from ...services.cleanup_service import CleanupService
from ...services.database_service import db_service
from ...services.luxury_guide_service import LuxuryGuideService
from ...database import TripDatabase
from ...utils.environment import load_project_env
from ...utils.error_handling import ConfigurationError

# Load environment
load_project_env()

logger = logging.getLogger(__name__)


class ServiceContainer:
    """
    Dependency injection container for managing service instances
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
        self._locked_services: set = set()

    def initialize(self, config: Any) -> None:
        """
        Initialize all services with configuration

        Args:
            config: Application configuration object
        """
        if self._initialized:
            return

        try:
            # Core services
            self._services['pdf_processor'] = PDFProcessor()
            self._services['llm_extractor'] = LLMExtractor()
            self._services['enhanced_guide_service'] = EnhancedGuideService()
            self._services['fast_guide_service'] = FastGuideService()
            self._services['optimized_guide_service'] = OptimizedGuideService()
            
            # Optional services - only initialize if API keys are available
            try:
                self._services['immediate_guide_generator'] = ImmediateGuideGenerator()
                logger.info("Immediate guide generator initialized")
            except Exception as e:
                logger.warning(f"Immediate guide generator not available: {e}")
                self._services['immediate_guide_generator'] = None
            
            self._services['database_service'] = db_service
            # Lock the database service to prevent override
            self._locked_services = {'database_service'}
            self._services['trip_database'] = TripDatabase()
            self._services['luxury_guide_service'] = LuxuryGuideService()

            # Cleanup service with configuration
            self._services['cleanup_service'] = CleanupService(
                uploads_dir=config.UPLOAD_DIR,
                outputs_dir=config.OUTPUT_DIR,
                ttl_hours=24
            )

            self._initialized = True
            logger.info("Service container initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize service container: {e}")
            raise ConfigurationError(f"Service initialization failed: {e}")

    def get_service(self, service_name: str) -> Any:
        """
        Get service instance by name

        Args:
            service_name: Name of the service

        Returns:
            Service instance

        Raises:
            ConfigurationError: If service not found or container not initialized
        """
        if not self._initialized:
            raise ConfigurationError("Service container not initialized")

        if service_name not in self._services:
            raise ConfigurationError(f"Service not found: {service_name}")

        return self._services[service_name]

    def set_service(self, service_name: str, service: Any) -> None:
        """Set a service (with lock protection)"""
        if service_name in self._locked_services:
            logger.warning(f"Attempted to override locked service: {service_name}")
            return
        self._services[service_name] = service

    def get_pdf_processor(self) -> PDFProcessor:
        """Get PDF processor service"""
        return self.get_service('pdf_processor')

    def get_llm_extractor(self) -> LLMExtractor:
        """Get LLM extractor service"""
        return self.get_service('llm_extractor')

    def get_enhanced_guide_service(self) -> EnhancedGuideService:
        """Get enhanced guide service"""
        return self.get_service('enhanced_guide_service')

    def get_fast_guide_service(self) -> FastGuideService:
        """Get fast guide service"""
        return self.get_service('fast_guide_service')

    def get_optimized_guide_service(self) -> OptimizedGuideService:
        """Get optimized guide service"""
        return self.get_service('optimized_guide_service')

    def get_immediate_guide_generator(self) -> ImmediateGuideGenerator:
        """Get immediate guide generator"""
        return self.get_service('immediate_guide_generator')

    def get_cleanup_service(self) -> CleanupService:
        """Get cleanup service"""
        return self.get_service('cleanup_service')

    def get_database_service(self):
        """Get database service"""
        service = self.get_service('database_service')
        # Ensure we're getting the correct DatabaseService instance
        from ...services.database_service import DatabaseService
        if not isinstance(service, DatabaseService):
            logger.error(f"Database service type mismatch: expected DatabaseService, got {type(service)}")
            # Force return the correct service
            return self._services['database_service']
        return service

    def get_trip_database(self) -> TripDatabase:
        """Get trip database"""
        return self.get_service('trip_database')


# Global container instance
container = ServiceContainer()
