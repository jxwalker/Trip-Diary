"""
Configuration package for TripCraft AI
Centralized configuration management with environment-specific settings
"""

from .settings import Settings, get_settings
from .database import DatabaseConfig
from .api import APIConfig
from .services import ServicesConfig
from .logging import LoggingConfig

__all__ = [
    'Settings',
    'get_settings',
    'DatabaseConfig',
    'APIConfig', 
    'ServicesConfig',
    'LoggingConfig',
]

# Global settings instance
settings = get_settings()
