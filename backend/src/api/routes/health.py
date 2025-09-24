"""
Health routes for environment and secrets diagnostics
"""
import os
import logging
from typing import Any, Dict

from fastapi import APIRouter

from ...services.enhanced_redis_cache import cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"]) 


def _present(key: str) -> bool:
    value = os.getenv(key)
    return bool(value and value.strip())


@router.get("/health/secrets")
async def health_secrets() -> Dict[str, Any]:
    """
    Report presence (not values) of required and optional secrets, plus
    cache status.
    """
    required = {
        "PERPLEXITY_API_KEY": _present("PERPLEXITY_API_KEY"),
        "OPENWEATHER_API_KEY": _present("OPENWEATHER_API_KEY"),
        "GOOGLE_MAPS_API_KEY": _present("GOOGLE_MAPS_API_KEY"),
    }
    optional = {
        "OPENAI_API_KEY": _present("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": _present("ANTHROPIC_API_KEY"),
        "TICKETMASTER_API_KEY": _present("TICKETMASTER_API_KEY"),
        "EVENTBRITE_TOKEN": _present("EVENTBRITE_TOKEN"),
    }

    cache_stats = await cache_manager.get_stats()

    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "required": required,
        "optional": optional,
        "cache": {
            "connected": cache_stats.get("connected", False),
            "host": cache_stats.get("host"),
            "total_keys": cache_stats.get("total_keys"),
            "hit_rate": cache_stats.get("hit_rate"),
            "namespaces": cache_stats.get("namespaces", {}),
        }
    }
