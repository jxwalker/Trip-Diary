"""
Centralized Configuration Management for Trip Diary
Handles environment variables, defaults, and validation
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration management"""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration with optional custom env file"""
        self._load_environment(env_file)
        self._validate_required_config()
    
    def _load_environment(self, env_file: Optional[str] = None):
        """Load environment variables from .env file"""
        if env_file:
            env_path = Path(env_file)
        else:
            # Look for .env file in project root (parent of backend directory)
            # __file__ is backend/config.py, so parent.parent gets us to project root
            backend_dir = Path(__file__).parent  # backend/
            project_root = backend_dir.parent    # trip-diary/
            env_path = project_root / '.env'
        
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
        else:
            logger.warning(f"No .env file found at {env_path}")
    
    def _validate_required_config(self):
        """Validate that required configuration is present"""
        missing_keys = []
        
        # Check for at least one LLM provider
        llm_providers = [
            self.OPENAI_API_KEY,
            self.ANTHROPIC_API_KEY,
            self.XAI_API_KEY,
            self.SAMBANOVA_API_KEY
        ]
        
        if not any(llm_providers):
            missing_keys.append("At least one LLM API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, XAI_API_KEY, or SAMBANOVA_API_KEY)")
        
        if missing_keys:
            raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")
    
    # Server Configuration
    @property
    def HOST(self) -> str:
        return os.getenv('HOST', '0.0.0.0')
    
    @property
    def PORT(self) -> int:
        return int(os.getenv('PORT', '8000'))
    
    @property
    def ENVIRONMENT(self) -> str:
        return os.getenv('ENVIRONMENT', 'development')
    
    @property
    def DEBUG(self) -> bool:
        return os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Frontend Configuration
    @property
    def FRONTEND_URL(self) -> str:
        if self.ENVIRONMENT == 'production':
            return os.getenv('FRONTEND_URL', 'https://yourdomain.com')
        return os.getenv('FRONTEND_URL', f'http://localhost:3000')
    
    @property
    def BACKEND_URL(self) -> str:
        if self.ENVIRONMENT == 'production':
            return os.getenv('BACKEND_URL', 'https://api.yourdomain.com')
        return os.getenv('BACKEND_URL', f'http://localhost:{self.PORT}')
    
    # LLM Provider API Keys
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def ANTHROPIC_API_KEY(self) -> Optional[str]:
        return os.getenv('ANTHROPIC_API_KEY')
    
    @property
    def XAI_API_KEY(self) -> Optional[str]:
        return os.getenv('XAI_API_KEY')
    
    @property
    def SAMBANOVA_API_KEY(self) -> Optional[str]:
        return os.getenv('SAMBANOVA_API_KEY')
    
    @property
    def PERPLEXITY_API_KEY(self) -> Optional[str]:
        return os.getenv('PERPLEXITY_API_KEY')
    
    @property
    def PERPLEXITY_MODEL(self) -> str:
        return os.getenv('PERPLEXITY_MODEL', 'sonar')
    
    # Google APIs
    @property
    def GOOGLE_MAPS_API_KEY(self) -> Optional[str]:
        return os.getenv('GOOGLE_MAPS_API_KEY')
    
    @property
    def GOOGLE_SEARCH_API_KEY(self) -> Optional[str]:
        return os.getenv('GOOGLE_SEARCH_API_KEY')
    
    @property
    def GOOGLE_CUSTOM_SEARCH_ENGINE_ID(self) -> Optional[str]:
        return os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    
    @property
    def YOUTUBE_API_KEY(self) -> Optional[str]:
        return os.getenv('YOUTUBE_API_KEY')
    
    # Weather API
    @property
    def OPENWEATHER_API_KEY(self) -> Optional[str]:
        return os.getenv('OPENWEATHER_API_KEY')
    
    # Other APIs
    @property
    def FIRECRAWL_API_KEY(self) -> Optional[str]:
        return os.getenv('FIRECRAWL_API_KEY')
    
    @property
    def NEWS_API_KEY(self) -> Optional[str]:
        return os.getenv('NEWS_API_KEY')
    
    @property
    def SERPER_API_KEY(self) -> Optional[str]:
        return os.getenv('SERPER_API_KEY')
    
    @property
    def LANGSMITH_API_KEY(self) -> Optional[str]:
        return os.getenv('LANGSMITH_API_KEY')
    
    # Database Configuration
    @property
    def DATABASE_URL(self) -> str:
        return os.getenv('DATABASE_URL', 'sqlite:///trip_diary.db')
    
    # File Storage Configuration
    @property
    def UPLOAD_DIR(self) -> str:
        return os.getenv('UPLOAD_DIR', 'uploads')
    
    @property
    def OUTPUT_DIR(self) -> str:
        return os.getenv('OUTPUT_DIR', 'output')
    
    @property
    def MAX_FILE_SIZE(self) -> int:
        return int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB default
    
    # CORS Configuration
    @property
    def ALLOWED_ORIGINS(self) -> list:
        if self.ENVIRONMENT == 'production':
            origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
            return [origin.strip() for origin in origins if origin.strip()]
        else:
            # Development defaults
            return [
                self.FRONTEND_URL,
                'http://localhost:3000',
                'http://localhost:3001',
                'http://127.0.0.1:3000',
            ]
    
    # Logging Configuration
    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def LOG_FORMAT(self) -> str:
        return os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Testing Configuration
    @property
    def TESTING(self) -> bool:
        return os.getenv('TESTING', 'false').lower() == 'true'
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary (excluding sensitive keys)"""
        sensitive_keys = {
            'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'XAI_API_KEY', 'SAMBANOVA_API_KEY',
            'PERPLEXITY_API_KEY', 'GOOGLE_MAPS_API_KEY', 'GOOGLE_SEARCH_API_KEY',
            'YOUTUBE_API_KEY', 'OPENWEATHER_API_KEY', 'FIRECRAWL_API_KEY',
            'NEWS_API_KEY', 'SERPER_API_KEY', 'LANGSMITH_API_KEY'
        }
        
        config = {}
        for attr in dir(self):
            if not attr.startswith('_') and not callable(getattr(self, attr)):
                key = attr
                value = getattr(self, key)
                if key in sensitive_keys:
                    config[key] = '***' if value else None
                else:
                    config[key] = value
        
        return config

# Global configuration instance
config = Config()
