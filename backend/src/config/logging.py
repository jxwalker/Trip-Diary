"""
Logging Configuration
"""
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
import logging


class LoggingConfig(BaseSettings):
    """Logging configuration"""
    
    # Basic logging settings
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S", env="LOG_DATE_FORMAT"
    )
    
    # File logging
    file_enabled: bool = Field(default=True, env="LOG_FILE_ENABLED")
    file_path: str = Field(default="logs", env="LOG_FILE_PATH")
    file_name: str = Field(default="tripcraft.log", env="LOG_FILE_NAME")
    file_max_size_mb: int = Field(default=10, env="LOG_FILE_MAX_SIZE_MB")
    file_backup_count: int = Field(default=5, env="LOG_FILE_BACKUP_COUNT")
    
    # Console logging
    console_enabled: bool = Field(default=True, env="LOG_CONSOLE_ENABLED")
    console_level: str = Field(default="INFO", env="LOG_CONSOLE_LEVEL")
    
    # Structured logging
    structured_enabled: bool = Field(
        default=False, env="LOG_STRUCTURED_ENABLED"
    )
    structured_format: str = Field(
        default="json", env="LOG_STRUCTURED_FORMAT"
    )  # json, logfmt
    
    # Request logging
    request_logging_enabled: bool = Field(
        default=True, env="LOG_REQUEST_ENABLED"
    )
    request_log_body: bool = Field(default=False, env="LOG_REQUEST_BODY")
    request_log_headers: bool = Field(default=False, env="LOG_REQUEST_HEADERS")
    
    # Performance logging
    performance_logging_enabled: bool = Field(
        default=True, env="LOG_PERFORMANCE_ENABLED"
    )
    slow_request_threshold_ms: int = Field(
        default=1000, env="LOG_SLOW_REQUEST_THRESHOLD_MS"
    )
    
    # External service logging
    external_service_logging_enabled: bool = Field(
        default=True, env="LOG_EXTERNAL_SERVICE_ENABLED"
    )
    
    # Security logging
    security_logging_enabled: bool = Field(
        default=True, env="LOG_SECURITY_ENABLED"
    )
    
    # Logger-specific levels
    logger_levels: Dict[str, str] = Field(
        default={
            "uvicorn": "INFO",
            "uvicorn.access": "INFO",
            "fastapi": "INFO",
            "httpx": "WARNING",
            "openai": "WARNING",
            "anthropic": "WARNING",
        },
        env="LOG_LOGGER_LEVELS"
    )
    
    @validator('level', 'console_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    @validator('structured_format')
    def validate_structured_format(cls, v):
        """Validate structured format"""
        valid_formats = ['json', 'logfmt']
        if v not in valid_formats:
            raise ValueError(
                f'Structured format must be one of: {valid_formats}'
            )
        return v
    
    def get_log_level(self) -> int:
        """Get numeric log level"""
        return getattr(logging, self.level)
    
    def get_console_log_level(self) -> int:
        """Get numeric console log level"""
        return getattr(logging, self.console_level)
    
    def get_file_path(self) -> str:
        """Get full file path"""
        return f"{self.file_path}/{self.file_name}"
    
    def get_file_max_bytes(self) -> int:
        """Get file max size in bytes"""
        return self.file_max_size_mb * 1024 * 1024
    
    def should_log_slow_request(self, duration_ms: float) -> bool:
        """Check if request should be logged as slow"""
        return (self.performance_logging_enabled and 
                duration_ms > self.slow_request_threshold_ms)
    
    def get_logger_config(self) -> Dict[str, Any]:
        """Get complete logger configuration"""
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.format,
                    "datefmt": self.date_format,
                },
            },
            "handlers": {},
            "loggers": {
                "": {  # Root logger
                    "level": self.level,
                    "handlers": [],
                },
            },
        }
        
        # Add console handler
        if self.console_enabled:
            config["handlers"]["console"] = {
                "class": "logging.StreamHandler",
                "level": self.console_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            }
            config["loggers"][""]["handlers"].append("console")
        
        # Add file handler
        if self.file_enabled:
            config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": self.level,
                "formatter": "default",
                "filename": self.get_file_path(),
                "maxBytes": self.get_file_max_bytes(),
                "backupCount": self.file_backup_count,
            }
            config["loggers"][""]["handlers"].append("file")
        
        # Add structured logging if enabled
        if self.structured_enabled:
            if self.structured_format == "json":
                config["formatters"]["json"] = {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                }
                config["handlers"]["structured"] = {
                    "class": "logging.StreamHandler",
                    "level": self.level,
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                }
                config["loggers"][""]["handlers"].append("structured")
        
        # Add logger-specific levels
        for logger_name, level in self.logger_levels.items():
            config["loggers"][logger_name] = {
                "level": level,
                "handlers": [],
                "propagate": True,
            }
        
        return config
    
    class Config:
        env_prefix = "LOG_"
