"""
Performance Optimization Service
Advanced caching, connection pooling, and performance monitoring
"""
import asyncio
import time
import hashlib
import pickle
from typing import Dict, Any, Optional, Callable, TypeVar, Union, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import wraps
import logging

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def access(self) -> None:
        """Record cache access"""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    cache_hits: int = 0
    cache_misses: int = 0
    cache_size: int = 0
    avg_response_time_ms: float = 0.0
    total_requests: int = 0
    active_connections: int = 0
    memory_usage_mb: float = 0.0
    
    @property
    def cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_size": self.cache_size,
            "cache_hit_ratio": self.cache_hit_ratio,
            "avg_response_time_ms": self.avg_response_time_ms,
            "total_requests": self.total_requests,
            "active_connections": self.active_connections,
            "memory_usage_mb": self.memory_usage_mb
        }


class MemoryCache:
    """High-performance in-memory cache"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self.metrics = PerformanceMetrics()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            self.metrics.cache_misses += 1
            return None
        
        entry = self._cache[key]
        
        if entry.is_expired():
            await self.delete(key)
            self.metrics.cache_misses += 1
            return None
        
        entry.access()
        self._update_access_order(key)
        self.metrics.cache_hits += 1
        return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        entry = CacheEntry(value=value, created_at=datetime.now(), expires_at=expires_at)
        
        # Remove old entry if exists
        if key in self._cache:
            self._access_order.remove(key)
        
        # Evict if at capacity
        while len(self._cache) >= self.max_size:
            await self._evict_lru()
        
        self._cache[key] = entry
        self._access_order.append(key)
        self.metrics.cache_size = len(self._cache)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            self._access_order.remove(key)
            self.metrics.cache_size = len(self._cache)
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._access_order.clear()
        self.metrics.cache_size = 0
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            await self.delete(key)
        
        return len(expired_keys)
    
    def _update_access_order(self, key: str) -> None:
        """Update LRU access order"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self._access_order:
            lru_key = self._access_order[0]
            await self.delete(lru_key)


class RedisCache:
    """Redis-based distributed cache"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 300):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._redis: Optional[redis.Redis] = None
        self.metrics = PerformanceMetrics()
    
    async def initialize(self) -> None:
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis library not available")
        
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=False)
            await self._redis.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self._redis:
            return None
        
        try:
            data = await self._redis.get(key)
            if data is None:
                self.metrics.cache_misses += 1
                return None
            
            value = pickle.loads(data)
            self.metrics.cache_hits += 1
            return value
            
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.metrics.cache_misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache"""
        if not self._redis:
            return
        
        try:
            data = pickle.dumps(value)
            if ttl is None:
                ttl = self.default_ttl
            
            if ttl > 0:
                await self._redis.setex(key, ttl, data)
            else:
                await self._redis.set(key, data)
                
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        if not self._redis:
            return False
        
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        if not self._redis:
            return
        
        try:
            await self._redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup Redis connection"""
        if self._redis:
            await self._redis.close()


class PerformanceOptimizer:
    """Main performance optimization service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.memory_cache = MemoryCache(
            max_size=1000,
            default_ttl=300
        )
        self.redis_cache: Optional[RedisCache] = None
        self.metrics = PerformanceMetrics()
        self._response_times: List[float] = []
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> None:
        """Initialize performance optimizer"""
        try:
            # Initialize Redis cache if available
            if REDIS_AVAILABLE and hasattr(self.settings, 'redis_url'):
                self.redis_cache = RedisCache(self.settings.redis_url)
                await self.redis_cache.initialize()
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Performance optimizer initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance optimizer: {e}")
    
    async def get_cache(self, key: str, use_redis: bool = True) -> Optional[Any]:
        """Get value from cache (Redis first, then memory)"""
        # Try Redis first if available
        if use_redis and self.redis_cache:
            value = await self.redis_cache.get(key)
            if value is not None:
                return value
        
        # Fallback to memory cache
        return await self.memory_cache.get(key)
    
    async def set_cache(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_redis: bool = True
    ) -> None:
        """Set value in cache (both Redis and memory)"""
        # Set in memory cache
        await self.memory_cache.set(key, value, ttl)
        
        # Set in Redis if available
        if use_redis and self.redis_cache:
            await self.redis_cache.set(key, value, ttl)
    
    async def delete_cache(self, key: str, use_redis: bool = True) -> bool:
        """Delete key from cache"""
        memory_result = await self.memory_cache.delete(key)
        redis_result = True
        
        if use_redis and self.redis_cache:
            redis_result = await self.redis_cache.delete(key)
        
        return memory_result or redis_result
    
    async def clear_cache(self, use_redis: bool = True) -> None:
        """Clear all cache entries"""
        await self.memory_cache.clear()
        
        if use_redis and self.redis_cache:
            await self.redis_cache.clear()
    
    def record_response_time(self, response_time_ms: float) -> None:
        """Record response time for metrics"""
        self._response_times.append(response_time_ms)
        
        # Keep only recent response times (last 1000)
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]
        
        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.avg_response_time_ms = sum(self._response_times) / len(self._response_times)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        # Combine metrics from all caches
        combined_metrics = PerformanceMetrics(
            cache_hits=self.memory_cache.metrics.cache_hits,
            cache_misses=self.memory_cache.metrics.cache_misses,
            cache_size=self.memory_cache.metrics.cache_size,
            avg_response_time_ms=self.metrics.avg_response_time_ms,
            total_requests=self.metrics.total_requests
        )
        
        if self.redis_cache:
            combined_metrics.cache_hits += self.redis_cache.metrics.cache_hits
            combined_metrics.cache_misses += self.redis_cache.metrics.cache_misses
        
        return {
            "performance_metrics": combined_metrics.to_dict(),
            "memory_cache": self.memory_cache.metrics.to_dict(),
            "redis_cache": self.redis_cache.metrics.to_dict() if self.redis_cache else None,
            "response_time_percentiles": self._calculate_percentiles(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_percentiles(self) -> Dict[str, float]:
        """Calculate response time percentiles"""
        if not self._response_times:
            return {}
        
        sorted_times = sorted(self._response_times)
        length = len(sorted_times)
        
        return {
            "p50": sorted_times[int(length * 0.5)],
            "p90": sorted_times[int(length * 0.9)],
            "p95": sorted_times[int(length * 0.95)],
            "p99": sorted_times[int(length * 0.99)],
            "min": min(sorted_times),
            "max": max(sorted_times)
        }
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired cache entries"""
        while True:
            try:
                # Cleanup expired entries every 5 minutes
                await asyncio.sleep(300)
                
                expired_count = await self.memory_cache.cleanup_expired()
                if expired_count > 0:
                    logger.debug(f"Cleaned up {expired_count} expired cache entries")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup performance optimizer"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_cache:
            await self.redis_cache.cleanup()
        
        logger.info("Performance optimizer cleanup completed")


# Decorators for caching and performance monitoring
def cache_result(ttl: int = 300, key_prefix: str = "", use_redis: bool = True):
    """Decorator to cache function results"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await performance_optimizer.get_cache(cache_key, use_redis)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await performance_optimizer.set_cache(cache_key, result, ttl, use_redis)
            
            return result
        return wrapper
    return decorator


def monitor_performance(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            response_time_ms = (time.time() - start_time) * 1000
            performance_optimizer.record_response_time(response_time_ms)
    
    return wrapper


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()
