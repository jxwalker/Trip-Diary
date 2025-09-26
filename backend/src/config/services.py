"""
Services Configuration
"""
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any


class ServicesConfig(BaseSettings):
    """External services configuration"""
    
    # OpenAI Configuration (fallback for vision tasks)
    openai_enabled: bool = Field(default=True, env="OPENAI_ENABLED")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_vision_model: str = Field(default="gpt-4o-mini", env="OPENAI_VISION_MODEL")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_timeout: int = Field(default=60, env="OPENAI_TIMEOUT")

    # Anthropic Configuration (fallback)
    anthropic_enabled: bool = Field(default=True, env="ANTHROPIC_ENABLED")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-haiku-20240307", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=4000, env="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(default=0.7, env="ANTHROPIC_TEMPERATURE")
    anthropic_timeout: int = Field(default=60, env="ANTHROPIC_TIMEOUT")

    # Perplexity Configuration
    perplexity_enabled: bool = Field(default=True, env="PERPLEXITY_ENABLED")
    perplexity_api_key: Optional[str] = Field(default=None, env="PERPLEXITY_API_KEY")
    perplexity_model: str = Field(default="llama-3.1-sonar-small-128k-online", env="PERPLEXITY_MODEL")
    perplexity_max_tokens: int = Field(default=4000, env="PERPLEXITY_MAX_TOKENS")
    perplexity_temperature: float = Field(default=0.2, env="PERPLEXITY_TEMPERATURE")
    perplexity_timeout: int = Field(default=60, env="PERPLEXITY_TIMEOUT")

    openrouter_enabled: bool = Field(default=True, env="OPENROUTER_ENABLED")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="xai/grok-4-fast-free", env="OPENROUTER_MODEL")
    openrouter_max_tokens: int = Field(default=4000, env="OPENROUTER_MAX_TOKENS")
    openrouter_temperature: float = Field(default=0.7, env="OPENROUTER_TEMPERATURE")
    openrouter_timeout: int = Field(default=60, env="OPENROUTER_TIMEOUT")

    together_enabled: bool = Field(default=True, env="TOGETHER_ENABLED")
    together_api_key: Optional[str] = Field(default=None, env="TOGETHER_API_KEY")
    together_model: str = Field(default="meta-llama/Llama-3.2-3B-Instruct-Turbo", env="TOGETHER_MODEL")
    together_max_tokens: int = Field(default=4000, env="TOGETHER_MAX_TOKENS")
    together_temperature: float = Field(default=0.7, env="TOGETHER_TEMPERATURE")
    together_timeout: int = Field(default=60, env="TOGETHER_TIMEOUT")

    groq_enabled: bool = Field(default=True, env="GROQ_ENABLED")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", env="GROQ_MODEL")
    groq_max_tokens: int = Field(default=4000, env="GROQ_MAX_TOKENS")
    groq_temperature: float = Field(default=0.7, env="GROQ_TEMPERATURE")
    groq_timeout: int = Field(default=60, env="GROQ_TIMEOUT")

    primary_model_provider: str = Field(default="openrouter", env="PRIMARY_MODEL_PROVIDER")
    primary_model: str = Field(default="xai/grok-4-fast-free", env="PRIMARY_MODEL")
    
    # Google Places Configuration
    google_places_enabled: bool = Field(default=True, env="GOOGLE_PLACES_ENABLED")
    google_places_api_key: Optional[str] = Field(default=None, env="GOOGLE_PLACES_API_KEY")
    google_places_timeout: int = Field(default=30, env="GOOGLE_PLACES_TIMEOUT")
    
    # Weather Service Configuration
    weather_enabled: bool = Field(default=True, env="WEATHER_ENABLED")
    weather_api_key: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    weather_provider: str = Field(default="openweathermap", env="WEATHER_PROVIDER")
    weather_timeout: int = Field(default=30, env="WEATHER_TIMEOUT")
    
    # Maps Service Configuration
    maps_enabled: bool = Field(default=True, env="MAPS_ENABLED")
    maps_api_key: Optional[str] = Field(default=None, env="MAPS_API_KEY")
    maps_provider: str = Field(default="google", env="MAPS_PROVIDER")
    maps_timeout: int = Field(default=30, env="MAPS_TIMEOUT")
    
    # PDF Generation Configuration
    pdf_enabled: bool = Field(default=True, env="PDF_ENABLED")
    pdf_engine: str = Field(default="weasyprint", env="PDF_ENGINE")  # weasyprint, reportlab
    pdf_timeout: int = Field(default=120, env="PDF_TIMEOUT")
    
    # Image Processing Configuration
    image_processing_enabled: bool = Field(default=True, env="IMAGE_PROCESSING_ENABLED")
    image_max_size_mb: int = Field(default=10, env="IMAGE_MAX_SIZE_MB")
    image_allowed_formats: list = Field(
        default=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
        env="IMAGE_ALLOWED_FORMATS"
    )
    
    # File Processing Configuration
    file_processing_enabled: bool = Field(default=True, env="FILE_PROCESSING_ENABLED")
    file_max_size_mb: int = Field(default=50, env="FILE_MAX_SIZE_MB")
    file_allowed_formats: list = Field(
        default=["pdf", "txt", "docx", "jpg", "jpeg", "png"],
        env="FILE_ALLOWED_FORMATS"
    )
    
    # Retry Configuration
    retry_enabled: bool = Field(default=True, env="RETRY_ENABLED")
    retry_max_attempts: int = Field(default=3, env="RETRY_MAX_ATTEMPTS")
    retry_delay_seconds: float = Field(default=1.0, env="RETRY_DELAY_SECONDS")
    retry_backoff_factor: float = Field(default=2.0, env="RETRY_BACKOFF_FACTOR")
    
    @validator('openai_temperature', 'anthropic_temperature', 'perplexity_temperature')
    def validate_temperature(cls, v):
        """Validate temperature is between 0 and 2"""
        if not 0 <= v <= 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v
    
    @validator('weather_provider')
    def validate_weather_provider(cls, v):
        """Validate weather provider"""
        valid_providers = ['openweathermap', 'weatherapi']
        if v not in valid_providers:
            raise ValueError(f'Weather provider must be one of: {valid_providers}')
        return v
    
    @validator('maps_provider')
    def validate_maps_provider(cls, v):
        """Validate maps provider"""
        valid_providers = ['google', 'mapbox']
        if v not in valid_providers:
            raise ValueError(f'Maps provider must be one of: {valid_providers}')
        return v
    
    @validator('pdf_engine')
    def validate_pdf_engine(cls, v):
        """Validate PDF engine"""
        valid_engines = ['weasyprint', 'reportlab']
        if v not in valid_engines:
            raise ValueError(f'PDF engine must be one of: {valid_engines}')
        return v
    
    def get_enabled_services(self) -> Dict[str, bool]:
        """Get dictionary of enabled services (cheapest first)"""
        return {
            'openrouter': self.openrouter_enabled,
            'together': self.together_enabled,
            'groq': self.groq_enabled,
            'openai': self.openai_enabled,
            'anthropic': self.anthropic_enabled,
            'perplexity': self.perplexity_enabled,
            'google_places': self.google_places_enabled,
            'weather': self.weather_enabled,
            'maps': self.maps_enabled,
            'pdf': self.pdf_enabled,
            'image_processing': self.image_processing_enabled,
            'file_processing': self.file_processing_enabled,
        }
    
    def get_missing_api_keys(self) -> Dict[str, bool]:
        """Get dictionary of missing API keys for enabled services"""
        missing = {}
        
        if self.openrouter_enabled and not self.openrouter_api_key:
            missing['openrouter'] = True
        if self.together_enabled and not self.together_api_key:
            missing['together'] = True
        if self.groq_enabled and not self.groq_api_key:
            missing['groq'] = True
        if self.openai_enabled and not self.openai_api_key:
            missing['openai'] = True
        if self.anthropic_enabled and not self.anthropic_api_key:
            missing['anthropic'] = True
        if self.perplexity_enabled and not self.perplexity_api_key:
            missing['perplexity'] = True
        if self.google_places_enabled and not self.google_places_api_key:
            missing['google_places'] = True
        if self.weather_enabled and not self.weather_api_key:
            missing['weather'] = True
        if self.maps_enabled and not self.maps_api_key:
            missing['maps'] = True
            
        return missing
    
    def validate_required_services(self) -> bool:
        """Validate that required services have API keys"""
        missing = self.get_missing_api_keys()
        if missing:
            service_names = ', '.join(missing.keys())
            raise ValueError(f'Missing API keys for enabled services: {service_names}')
        return True

    def get_cheapest_model(self) -> tuple[str, str]:
        """Get the cheapest available model provider and model name"""
        if self.openrouter_enabled and self.openrouter_api_key:
            return ("openrouter", self.openrouter_model)
        if self.together_enabled and self.together_api_key:
            return ("together", self.together_model)
        if self.groq_enabled and self.groq_api_key:
            return ("groq", self.groq_model)
        if self.openai_enabled and self.openai_api_key:
            return ("openai", self.openai_model)
        if self.anthropic_enabled and self.anthropic_api_key:
            return ("anthropic", self.anthropic_model)
        if self.perplexity_enabled and self.perplexity_api_key:
            return ("perplexity", self.perplexity_model)
        return ("openai", "gpt-4o-mini")
    
    class Config:
        env_prefix = "SERVICE_"
