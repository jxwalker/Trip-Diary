"""
Redis Cache Service for High-Performance API Response Caching
NO MOCKS - Only caches real API responses
"""
import json
import hashlib
import logging
from typing import Optional, Any, Dict
import redis
from redis import asyncio as redis_async
from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class RedisCacheService:
    """High-performance Redis caching for API responses"""
    
    def __init__(self):
        # Redis configuration
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        
        self.redis_client = None
        self.connected = False
        
        # Cache TTLs (in seconds)
        self.ttls = {
            "perplexity_content": 3600 * 6,    # 6 hours for content
            "weather": 3600,                    # 1 hour for weather
            "neighborhoods": 3600 * 24 * 7,     # 1 week for neighborhoods
            "events": 3600 * 12,                # 12 hours for events
            "complete_guide": 3600 * 2,         # 2 hours for complete guides
        }
    
    async def connect(self):
        """Connect to Redis"""
        if self.connected:
            return True
            
        try:
            self.redis_client = redis_async.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Test connection
            await self.redis_client.ping()
            self.connected = True
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
            return True
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Continuing without cache.")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate a unique cache key"""
        # Sort kwargs for consistent key generation
        key_data = f"{prefix}:" + json.dumps(kwargs, sort_keys=True)
        hash_digest = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"tripdiary:{prefix}:{hash_digest}"
    
    async def get(self, prefix: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached data if available"""
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return None
        
        try:
            key = self._generate_key(prefix, **kwargs)
            data = await self.redis_client.get(key)
            
            if data:
                logger.info(f"Cache HIT: {key}")
                return json.loads(data)
            else:
                logger.debug(f"Cache MISS: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, prefix: str, data: Dict[str, Any], ttl: Optional[int] = None, **kwargs):
        """Cache data with TTL"""
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return False
        
        try:
            key = self._generate_key(prefix, **kwargs)
            
            # Use default TTL if not specified
            if ttl is None:
                ttl = self.ttls.get(prefix, 3600)  # Default 1 hour
            
            # Store as JSON
            json_data = json.dumps(data)
            
            # Set with expiration
            await self.redis_client.setex(
                key,
                ttl,
                json_data
            )
            
            logger.info(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, prefix: str, **kwargs):
        """Delete cached data"""
        if not self.connected:
            return False
        
        try:
            key = self._generate_key(prefix, **kwargs)
            result = await self.redis_client.delete(key)
            logger.info(f"Cache DELETE: {key} (deleted: {result})")
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching a pattern"""
        if not self.connected:
            return 0
        
        try:
            # Find all keys matching pattern
            keys = []
            async for key in self.redis_client.scan_iter(f"tripdiary:{pattern}:*"):
                keys.append(key)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Cache CLEAR: Deleted {deleted} keys matching {pattern}")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return {"connected": False}
        
        try:
            info = await self.redis_client.info("stats")
            memory = await self.redis_client.info("memory")
            
            # Count keys by pattern
            patterns = ["perplexity_content", "weather", "neighborhoods", "complete_guide"]
            key_counts = {}
            
            for pattern in patterns:
                count = 0
                async for _ in self.redis_client.scan_iter(f"tripdiary:{pattern}:*"):
                    count += 1
                key_counts[pattern] = count
            
            return {
                "connected": True,
                "total_keys": await self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)) * 100, 
                    2
                ),
                "memory_used": memory.get("used_memory_human", "0"),
                "keys_by_type": key_counts
            }
            
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {"connected": False, "error": str(e)}

# Global instance
cache_service = RedisCacheService()