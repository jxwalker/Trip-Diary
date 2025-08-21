"""
FastAPI dependency functions for service injection
"""
from fastapi import Depends
from typing import Annotated

from .container import container
from ...services.pdf_processor import PDFProcessor
from ...services.llm_extractor import LLMExtractor
from ...services.enhanced_guide_service import EnhancedGuideService
from ...services.fast_guide_service import FastGuideService
from ...services.optimized_guide_service import OptimizedGuideService
from ...services.immediate_guide_generator import ImmediateGuideGenerator
from ...services.cleanup_service import CleanupService
from ...services.database_service import DatabaseService
from ...services.luxury_guide_service import LuxuryGuideService
from ...database import TripDatabase


def get_pdf_processor() -> PDFProcessor:
    """Dependency function for PDF processor"""
    return container.get_pdf_processor()


def get_llm_extractor() -> LLMExtractor:
    """Dependency function for LLM extractor"""
    return container.get_llm_extractor()


def get_enhanced_guide_service() -> EnhancedGuideService:
    """Dependency function for enhanced guide service"""
    return container.get_enhanced_guide_service()


def get_fast_guide_service() -> FastGuideService:
    """Dependency function for fast guide service"""
    return container.get_fast_guide_service()


def get_optimized_guide_service() -> OptimizedGuideService:
    """Dependency function for optimized guide service"""
    return container.get_optimized_guide_service()


def get_immediate_guide_generator() -> ImmediateGuideGenerator:
    """Dependency function for immediate guide generator"""
    return container.get_immediate_guide_generator()


def get_cleanup_service() -> CleanupService:
    """Dependency function for cleanup service"""
    return container.get_cleanup_service()


def get_database_service() -> DatabaseService:
    """Dependency function for database service"""
    return container.get_database_service()


def get_trip_database() -> TripDatabase:
    """Dependency function for trip database"""
    return container.get_trip_database()


def get_luxury_guide_service() -> LuxuryGuideService:
    """Dependency function for luxury guide service"""
    return container.get_service('luxury_guide_service')


# Type aliases for dependency injection
PDFProcessorDep = Annotated[PDFProcessor, Depends(get_pdf_processor)]
LLMExtractorDep = Annotated[LLMExtractor, Depends(get_llm_extractor)]
EnhancedGuideServiceDep = Annotated[EnhancedGuideService, Depends(get_enhanced_guide_service)]
FastGuideServiceDep = Annotated[FastGuideService, Depends(get_fast_guide_service)]
OptimizedGuideServiceDep = Annotated[OptimizedGuideService, Depends(get_optimized_guide_service)]
ImmediateGuideGeneratorDep = Annotated[ImmediateGuideGenerator, Depends(get_immediate_guide_generator)]
CleanupServiceDep = Annotated[CleanupService, Depends(get_cleanup_service)]
DatabaseServiceDep = Annotated[DatabaseService, Depends(get_database_service)]
TripDatabaseDep = Annotated[TripDatabase, Depends(get_trip_database)]
LuxuryGuideServiceDep = Annotated[LuxuryGuideService, Depends(get_luxury_guide_service)]
