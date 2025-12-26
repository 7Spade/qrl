"""
Redis cache module for trading bot.

Provides caching functionality using Redis for improved performance.
Supports optional Redis integration - falls back gracefully if unavailable.
"""
from typing import Optional, Any
import json
from datetime import timedelta
from src.core.config import CacheConfig


class CacheClient:
    """Redis cache client with fallback support."""
    
    def __init__(self, config: CacheConfig):
        """
        Initialize cache client.
        
        Args:
            config: Cache configuration
        """
        self.config = config
        self._redis = None
        self._enabled = False
        
        if config.redis_enabled and config.redis_url:
            self._init_redis()
    
    def _init_redis(self) -> None:
        """Initialize Redis connection."""
        try:
            import redis
            self._redis = redis.from_url(
                self.config.redis_url,
                decode_responses=True
            )
            # Test connection
            self._redis.ping()
            self._enabled = True
            print(f"✅ Redis connected: {self.config.redis_url.split('@')[-1]}")
        except ImportError:
            print("⚠️ Redis library not installed. Run: pip install redis")
            self._enabled = False
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self._enabled = False
    
    @property
    def enabled(self) -> bool:
        """Check if cache is enabled and connected."""
        return self._enabled
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/disabled
        """
        if not self._enabled:
            return None
        
        try:
            value = self._redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (uses config default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False
        
        try:
            ttl = ttl or self.config.cache_ttl
            self._redis.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False
        
        try:
            self._redis.delete(key)
            return True
        except Exception as e:
            print(f"⚠️ Cache delete error: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all cache entries.
        
        WARNING: This clears the entire Redis database.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._enabled:
            return False
        
        try:
            self._redis.flushdb()
            return True
        except Exception as e:
            print(f"⚠️ Cache clear error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self._enabled:
            return {
                "enabled": False,
                "status": "disabled"
            }
        
        try:
            info = self._redis.info()
            return {
                "enabled": True,
                "status": "connected",
                "keys": self._redis.dbsize(),
                "memory_used": info.get("used_memory_human", "N/A"),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            return {
                "enabled": True,
                "status": f"error: {e}"
            }
