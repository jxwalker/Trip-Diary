"""
Enhanced Redis Cache Manager
Comprehensive caching solution for all services
NO MOCKS - Real caching only
"""
import json
import hashlib
import logging
from typing import Optional, Any, Dict, List, Callable
from functools import wraps
import asyncio
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


class CacheConfig:
    """Cache configuration for different data types"""
    
    # TTL configurations in seconds
    TTL_CONFIG = {
        # API Response Caching
        "perplexity_search": 3600 * 6,     # 6 hours - search results don't change often
        "weather_data": 1800,               # 30 minutes - weather updates frequently
        "google_places": 3600 * 24,        # 24 hours - place info is stable
        "maps_directions": 3600 * 12,      # 12 hours - routes are relatively stable
        
        # Processed Data Caching
        "pdf_extraction": 3600 * 24 * 7,   # 1 week - PDFs don't change
        "parsed_travel_data": 3600 * 24,   # 24 hours - parsed data is stable
        "generated_guide": 3600 * 4,       # 4 hours - guides can be regenerated
        "enhanced_guide": 3600 * 2,        # 2 hours - enhanced guides update more
        "itinerary": 3600 * 6,             # 6 hours - itineraries are semi-stable
        
        # User Data Caching
        "user_preferences": 3600 * 24,     # 24 hours - preferences don't change often
        "trip_data": 3600 * 12,            # 12 hours - trip data updates
        "processing_status": 300,           # 5 minutes - status updates frequently
        
        # System Caching
        "llm_response": 3600,               # 1 hour - LLM responses can be cached
        "events_data": 3600 * 6,           # 6 hours - events update periodically
        "neighborhoods": 3600 * 24 * 7,    # 1 week - neighborhood info is stable
        "recommendations": 3600 * 12,      # 12 hours - recommendations update
    }


class EnhancedRedisCache:
    """Enhanced Redis caching with comprehensive features"""
    
    def __init__(self):
        # Redis configuration from environment
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        self.redis_max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", 50))
        
        self.redis_client = None
        self.connection_pool = None
        self.connected = False
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "sets": 0
        }
    
    async def connect(self) -> bool:
        """Establish Redis connection with pooling"""
        if self.connected:
            return True
        
        try:
            # Create connection pool for better performance
            self.connection_pool = redis_async.ConnectionPool(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                max_connections=self.redis_max_connections,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.redis_client = redis_async.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            self.connected = True
            
            logger.info(f"Redis connected: {self.redis_host}:{self.redis_port} (pool: {self.redis_max_connections})")
            
            # Start background tasks
            asyncio.create_task(self._health_check_loop())
            
            return True
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without cache.")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Gracefully disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            if self.connection_pool:
                await self.connection_pool.disconnect()
            self.connected = False
            logger.info("Redis disconnected")
    
    async def _health_check_loop(self):
        """Background health check for Redis connection"""
        while self.connected:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.redis_client.ping()
            except Exception as e:
                logger.error(f"Redis health check failed: {e}")
                self.connected = False
                # Try to reconnect
                await self.connect()
    
    def _generate_key(self, namespace: str, key_data: Dict[str, Any]) -> str:
        """Generate consistent cache key"""
        # Sort for consistency
        sorted_data = json.dumps(key_data, sort_keys=True)
        hash_digest = hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
        return f"tripdiary:{namespace}:{hash_digest}"
    
    async def get(
        self, 
        namespace: str, 
        key_data: Dict[str, Any],
        deserialize: bool = True
    ) -> Optional[Any]:
        """Get cached value with automatic deserialization"""
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return None
        
        try:
            cache_key = self._generate_key(namespace, key_data)
            value = await self.redis_client.get(cache_key)
            
            if value:
                self.stats["hits"] += 1
                logger.debug(f"Cache HIT: {namespace}")
                
                if deserialize:
                    return json.loads(value)
                return value
            else:
                self.stats["misses"] += 1
                logger.debug(f"Cache MISS: {namespace}")
                return None
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Cache GET error ({namespace}): {e}")
            return None
    
    async def set(
        self,
        namespace: str,
        key_data: Dict[str, Any],
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set cache value with automatic serialization"""
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return False
        
        try:
            cache_key = self._generate_key(namespace, key_data)
            
            # Use configured TTL or default
            if ttl is None:
                ttl = CacheConfig.TTL_CONFIG.get(namespace, 3600)
            
            # Serialize if needed
            if serialize:
                value = json.dumps(value)
            
            # Set with expiration
            await self.redis_client.setex(cache_key, ttl, value)
            
            self.stats["sets"] += 1
            logger.debug(f"Cache SET: {namespace} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Cache SET error ({namespace}): {e}")
            return False
    
    async def delete(self, namespace: str, key_data: Dict[str, Any]) -> bool:
        """Delete specific cache entry"""
        if not self.connected:
            return False
        
        try:
            cache_key = self._generate_key(namespace, key_data)
            result = await self.redis_client.delete(cache_key)
            logger.debug(f"Cache DELETE: {namespace} (deleted: {result})")
            return result > 0
            
        except Exception as e:
            logger.error(f"Cache DELETE error ({namespace}): {e}")
            return False
    
    async def clear_namespace(self, namespace: str) -> int:
        """Clear all entries in a namespace"""
        if not self.connected:
            return 0
        
        try:
            pattern = f"tripdiary:{namespace}:*"
            keys = []
            
            async for key in self.redis_client.scan_iter(pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Cache CLEAR: {namespace} ({deleted} keys)")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"Cache CLEAR error ({namespace}): {e}")
            return 0
    
    async def exists(self, namespace: str, key_data: Dict[str, Any]) -> bool:
        """Check if key exists in cache"""
        if not self.connected:
            return False
        
        try:
            cache_key = self._generate_key(namespace, key_data)
            return await self.redis_client.exists(cache_key) > 0
            
        except Exception as e:
            logger.error(f"Cache EXISTS error ({namespace}): {e}")
            return False
    
    async def get_ttl(self, namespace: str, key_data: Dict[str, Any]) -> int:
        """Get remaining TTL for a key"""
        if not self.connected:
            return -1
        
        try:
            cache_key = self._generate_key(namespace, key_data)
            ttl = await self.redis_client.ttl(cache_key)
            return ttl
            
        except Exception as e:
            logger.error(f"Cache TTL error ({namespace}): {e}")
            return -1
    
    async def extend_ttl(
        self, 
        namespace: str, 
        key_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Extend TTL for existing key"""
        if not self.connected:
            return False
        
        try:
            cache_key = self._generate_key(namespace, key_data)
            
            if ttl is None:
                ttl = CacheConfig.TTL_CONFIG.get(namespace, 3600)
            
            return await self.redis_client.expire(cache_key, ttl)
            
        except Exception as e:
            logger.error(f"Cache EXPIRE error ({namespace}): {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "connected": self.connected,
            "host": f"{self.redis_host}:{self.redis_port}",
            "local_stats": self.stats.copy()
        }
        
        if not self.connected:
            return stats
        
        try:
            # Get Redis server stats
            info = await self.redis_client.info("stats")
            memory = await self.redis_client.info("memory")
            
            # Count keys by namespace
            namespaces = list(CacheConfig.TTL_CONFIG.keys())
            namespace_counts = {}
            
            for ns in namespaces:
                count = 0
                async for _ in self.redis_client.scan_iter(f"tripdiary:{ns}:*"):
                    count += 1
                if count > 0:
                    namespace_counts[ns] = count
            
            stats.update({
                "total_keys": await self.redis_client.dbsize(),
                "server_hits": info.get("keyspace_hits", 0),
                "server_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                    2
                ),
                "memory_used": memory.get("used_memory_human", "0"),
                "memory_peak": memory.get("used_memory_peak_human", "0"),
                "namespaces": namespace_counts,
                "evicted_keys": info.get("evicted_keys", 0),
                "expired_keys": info.get("expired_keys", 0)
            })
            
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            stats["error"] = str(e)
        
        return stats
    
    async def batch_get(
        self,
        namespace: str,
        key_data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Batch get multiple keys"""
        if not self.connected:
            return {}
        
        try:
            # Generate all keys
            keys = [self._generate_key(namespace, kd) for kd in key_data_list]
            
            # Batch get
            values = await self.redis_client.mget(keys)
            
            # Map back to original key data
            result = {}
            for i, value in enumerate(values):
                if value:
                    key_str = json.dumps(key_data_list[i], sort_keys=True)
                    result[key_str] = json.loads(value)
            
            return result
            
        except Exception as e:
            logger.error(f"Batch GET error ({namespace}): {e}")
            return {}
    
    async def batch_set(
        self,
        namespace: str,
        items: List[tuple[Dict[str, Any], Any]],
        ttl: Optional[int] = None
    ) -> bool:
        """Batch set multiple keys"""
        if not self.connected:
            return False
        
        try:
            if ttl is None:
                ttl = CacheConfig.TTL_CONFIG.get(namespace, 3600)
            
            # Use pipeline for atomic batch operation
            pipe = self.redis_client.pipeline()
            
            for key_data, value in items:
                cache_key = self._generate_key(namespace, key_data)
                serialized = json.dumps(value)
                pipe.setex(cache_key, ttl, serialized)
            
            await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Batch SET error ({namespace}): {e}")
            return False


def cache_decorator(
    namespace: str,
    ttl: Optional[int] = None,
    key_generator: Optional[Callable] = None
):
    """Decorator for automatic caching of async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_generator:
                key_data = key_generator(*args, **kwargs)
            else:
                # Default key generation from args and kwargs
                key_data = {
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            
            # Try to get from cache
            cached = await cache_manager.get(namespace, key_data)
            if cached is not None:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache_manager.set(namespace, key_data, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache manager instance
cache_manager = EnhancedRedisCache()


# Export for backward compatibility
cache_service = cache_manager