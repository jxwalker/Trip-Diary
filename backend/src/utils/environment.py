"""
Environment utilities for consistent environment loading across services
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


def load_project_env() -> None:
    """
    Load environment variables from project root .env file
    This ensures consistent environment loading across all services
    """
    # Find project root (4 levels up from this file)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    env_path = project_root / '.env'

    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Fallback: look for .env in current working directory
        fallback_env = Path.cwd() / '.env'
        if fallback_env.exists():
            load_dotenv(fallback_env)


def get_api_key(service: str) -> Optional[str]:
    """
    Get API key for a specific service with consistent naming

    Args:
        service: Service name (openai, anthropic, perplexity, etc.)

    Returns:
        API key if found, None otherwise
    """
    key_name = f"{service.upper()}_API_KEY"
    return os.getenv(key_name)


def get_required_api_key(service: str) -> str:
    """
    Get required API key, raise error if not found

    Args:
        service: Service name

    Returns:
        API key

    Raises:
        ValueError: If API key is not found
    """
    key = get_api_key(service)
    if not key:
        raise ValueError(
            f"Missing required API key: {service.upper()}_API_KEY"
        )
    return key


def is_development() -> bool:
    """Check if running in development environment"""
    return os.getenv('ENVIRONMENT', 'development').lower() == 'development'


def is_testing() -> bool:
    """Check if running in testing environment"""
    return os.getenv('TESTING', 'false').lower() == 'true'
