"""
API Configuration
"""
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List


class APIConfig(BaseSettings):
    """API server configuration"""
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    
    # API metadata
    title: str = Field(default="TripCraft AI API", env="API_TITLE")
    description: str = Field(default="AI-powered travel planning and itinerary generation", env="API_DESCRIPTION")
    version: str = Field(default="1.0.0", env="API_VERSION")
    
    # CORS settings
    cors_enabled: bool = Field(default=True, env="CORS_ENABLED")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_HEADERS"
    )
    cors_expose_headers: List[str] = Field(
        default=["Content-Type", "X-Trip-ID", "X-Correlation-ID"],
        env="CORS_EXPOSE_HEADERS"
    )
    
    # Request/Response settings
    max_request_size: int = Field(default=50 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 50MB
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")  # 5 minutes
    
    # Documentation
    docs_enabled: bool = Field(default=True, env="API_DOCS_ENABLED")
    docs_url: str = Field(default="/docs", env="API_DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="API_REDOC_URL")
    openapi_url: str = Field(default="/openapi.json", env="API_OPENAPI_URL")
    
    class Config:
        env_prefix = "API_"
