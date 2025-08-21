"""
Main settings configuration with environment-specific overrides
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings

from .database import DatabaseConfig
from .api import APIConfig
from .services import ServicesConfig
from .logging import LoggingConfig


class Settings(BaseSettings):
    """Main application settings"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    api: APIConfig = Field(default_factory=APIConfig)
    
    # Database Configuration  
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    # Services Configuration
    services: ServicesConfig = Field(default_factory=ServicesConfig)
    
    # Logging Configuration
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # File Storage
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    output_dir: str = Field(default="outputs", env="OUTPUT_DIR")
    data_dir: str = Field(default="data", env="DATA_DIR")
    
    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Cleanup
    cleanup_enabled: bool = Field(default=True, env="CLEANUP_ENABLED")
    cleanup_interval_hours: int = Field(default=1, env="CLEANUP_INTERVAL_HOURS")
    file_ttl_hours: int = Field(default=24, env="FILE_TTL_HOURS")
    
    # Monitoring
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    metrics_enabled: bool = Field(default=False, env="METRICS_ENABLED")
    
    @validator('allowed_origins', pre=True)
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins from environment"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment value"""
        valid_envs = ['development', 'staging', 'production', 'testing']
        if v not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.environment == "testing"
    
    def get_upload_path(self) -> Path:
        """Get upload directory path"""
        return Path(self.upload_dir).resolve()
    
    def get_output_path(self) -> Path:
        """Get output directory path"""
        return Path(self.output_dir).resolve()
    
    def get_data_path(self) -> Path:
        """Get data directory path"""
        return Path(self.data_dir).resolve()
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        for path in [self.get_upload_path(), self.get_output_path(), self.get_data_path()]:
            path.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment-specific config files
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


class DevelopmentSettings(Settings):
    """Development environment settings"""
    environment: str = "development"
    debug: bool = True
    
    class Config(Settings.Config):
        env_file = ".env.development"


class ProductionSettings(Settings):
    """Production environment settings"""
    environment: str = "production"
    debug: bool = False
    
    # Override defaults for production
    rate_limit_requests: int = 1000
    cleanup_interval_hours: int = 6
    file_ttl_hours: int = 72
    
    class Config(Settings.Config):
        env_file = ".env.production"


class TestingSettings(Settings):
    """Testing environment settings"""
    environment: str = "testing"
    debug: bool = True
    
    # Use in-memory/temporary storage for tests
    upload_dir: str = "/tmp/test_uploads"
    output_dir: str = "/tmp/test_outputs"
    data_dir: str = "/tmp/test_data"
    
    # Disable external services for tests
    cleanup_enabled: bool = False
    rate_limit_enabled: bool = False
    
    class Config(Settings.Config):
        env_file = ".env.testing"


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary for debugging"""
    settings = get_settings()
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "api_host": settings.api.host,
        "api_port": settings.api.port,
        "database_path": str(settings.database.get_database_path()),
        "upload_dir": str(settings.get_upload_path()),
        "output_dir": str(settings.get_output_path()),
        "data_dir": str(settings.get_data_path()),
        "services_enabled": {
            "openai": settings.services.openai_enabled,
            "anthropic": settings.services.anthropic_enabled,
            "perplexity": settings.services.perplexity_enabled,
            "google_places": settings.services.google_places_enabled,
        },
        "features_enabled": {
            "rate_limiting": settings.rate_limit_enabled,
            "cleanup": settings.cleanup_enabled,
            "health_checks": settings.health_check_enabled,
            "metrics": settings.metrics_enabled,
        }
    }
