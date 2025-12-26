"""
Redis cache module for trading bot.

Provides caching functionality using Redis for improved performance.
Supports optional Redis integration - falls back gracefully if unavailable.
Includes automatic reconnection on connection loss.
"""
from typing import Optional, Any, List
import json
from datetime import timedelta, datetime
from decimal import Decimal
from src.core.config import CacheConfig


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for trading data types."""
    
    def default(self, obj):
        """Handle non-serializable objects."""
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)


class CacheClient:
    """Redis cache client with fallback support and automatic reconnection."""
    
    # Cache key version for schema migrations
    VERSION = "v1"
    
    def __init__(self, config: CacheConfig, namespace: str = "qrl"):
        """
        Initialize cache client.
        
        Args:
            config: Cache configuration
            namespace: Cache key namespace for environment separation (default: "qrl")
        """
        self.config = config
        self.namespace = namespace
        self._redis = None
        self._enabled = False
        self._connection_available = False
        
        if config.redis_enabled and config.redis_url:
            self._init_redis()
    
    def _init_redis(self) -> None:
        """Initialize Redis connection with max memory policy."""
        try:
            import redis
            self._redis = redis.from_url(
                self.config.redis_url,
                decode_responses=True
            )
            # Test connection
            self._redis.ping()
            
            # Set max memory policy to prevent unbounded growth
            try:
                self._redis.config_set('maxmemory-policy', 'allkeys-lru')
            except Exception as e:
                print(f"⚠️ Cannot set maxmemory-policy (may require admin): {e}")
            
            self._enabled = True
            self._connection_available = True
            print(f"✅ Redis connected: {self.config.redis_url.split('@')[-1]}")
        except ImportError:
            print("⚠️ Redis library not installed. Run: pip install redis")
            self._enabled = False
            self._connection_available = False
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self._enabled = False
            self._connection_available = False
    
    def _ensure_connection(self) -> bool:
        """
        Ensure Redis connection is available, attempt reconnection if needed.
        
        Returns:
            True if connected, False otherwise
        """
        if not self._enabled:
            return False
        
        if not self._connection_available or not self._redis:
            # Attempt reconnection
            try:
                self._init_redis()
            except Exception as e:
                print(f"⚠️ Redis reconnection failed: {e}")
                self._connection_available = False
                return False
        
        # Verify connection with ping
        try:
            self._redis.ping()
            self._connection_available = True
            return True
        except Exception as e:
            print(f"⚠️ Redis connection lost: {e}")
            self._connection_available = False
            return False
    
    @property
    def enabled(self) -> bool:
        """Check if cache is enabled and connected."""
        return self._enabled and self._ensure_connection()
    
    def _make_key(self, key: str) -> str:
        """
        Generate namespaced cache key with version.
        
        Args:
            key: Base cache key
            
        Returns:
            Namespaced and versioned cache key
        """
        return f"{self.namespace}:{self.VERSION}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache with automatic reconnection.
        
        Args:
            key: Cache key (will be namespaced automatically)
            
        Returns:
            Cached value or None if not found/disabled
        """
        if not self._ensure_connection():
            return None
        
        try:
            namespaced_key = self._make_key(key)
            value = self._redis.get(namespaced_key)
            if value:
                return json.loads(value)
        except json.JSONDecodeError as e:
            print(f"⚠️ Cache JSON decode error for key {key}: {e}")
            # Delete corrupted cache entry
            self.delete(key)
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
            self._connection_available = False
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with automatic reconnection.
        
        Args:
            key: Cache key (will be namespaced automatically)
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (uses config default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_connection():
            return False
        
        try:
            ttl = ttl or self.config.cache_ttl
            namespaced_key = self._make_key(key)
            self._redis.setex(
                namespaced_key,
                timedelta(seconds=ttl),
                json.dumps(value, cls=CustomJSONEncoder)
            )
            return True
        except (TypeError, ValueError) as e:
            print(f"⚠️ Cache serialization error for key {key}: {e}")
            return False
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")
            self._connection_available = False
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache with automatic reconnection.
        
        Args:
            key: Cache key (will be namespaced automatically)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_connection():
            return False
        
        try:
            namespaced_key = self._make_key(key)
            self._redis.delete(namespaced_key)
            return True
        except Exception as e:
            print(f"⚠️ Cache delete error: {e}")
            self._connection_available = False
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern with automatic reconnection.
        
        Args:
            pattern: Pattern to match (will be namespaced automatically)
                    Examples: "ticker:*", "ohlcv:QRLUSDT:*"
            
        Returns:
            Number of keys deleted, or 0 if failed
        """
        if not self._ensure_connection():
            return 0
        
        try:
            namespaced_pattern = self._make_key(pattern)
            keys = list(self._redis.scan_iter(match=namespaced_pattern))
            if keys:
                return self._redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"⚠️ Cache delete pattern error: {e}")
            self._connection_available = False
            return 0
    
    def clear_all(self) -> bool:
        """
        Clear all cache entries for this namespace with automatic reconnection.
        
        Only clears keys with the current namespace prefix, safe for shared Redis.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._ensure_connection():
            return False
        
        try:
            # Only delete keys with our namespace prefix
            pattern = f"{self.namespace}:{self.VERSION}:*"
            keys = list(self._redis.scan_iter(match=pattern))
            if keys:
                self._redis.delete(*keys)
            return True
        except Exception as e:
            print(f"⚠️ Cache clear error: {e}")
            self._connection_available = False
            return False
    
    def clear_symbol(self, symbol: str) -> int:
        """
        Clear all cache entries for a specific symbol.
        
        Args:
            symbol: Trading symbol (e.g., "QRL/USDT")
            
        Returns:
            Number of keys deleted
        """
        # Normalize symbol for pattern matching (replace / with escaped version)
        symbol_pattern = symbol.replace('/', '?')
        return self.delete_pattern(f"*{symbol_pattern}*")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics with automatic reconnection.
        
        Returns:
            Dictionary with cache stats
        """
        if not self._enabled:
            return {
                "enabled": False,
                "status": "disabled",
                "namespace": self.namespace,
                "version": self.VERSION
            }
        
        if not self._ensure_connection():
            return {
                "enabled": True,
                "status": "disconnected",
                "namespace": self.namespace,
                "version": self.VERSION
            }
        
        try:
            info = self._redis.info()
            
            # Count keys in our namespace
            pattern = f"{self.namespace}:{self.VERSION}:*"
            namespace_keys = len(list(self._redis.scan_iter(match=pattern, count=100)))
            
            return {
                "enabled": True,
                "status": "connected",
                "namespace": self.namespace,
                "version": self.VERSION,
                "keys_total": self._redis.dbsize(),
                "keys_namespace": namespace_keys,
                "memory_used": info.get("used_memory_human", "N/A"),
                "memory_peak": info.get("used_memory_peak_human", "N/A"),
                "maxmemory_policy": info.get("maxmemory_policy", "N/A"),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "evicted_keys": info.get("evicted_keys", 0),
            }
        except Exception as e:
            self._connection_available = False
            return {
                "enabled": True,
                "status": f"error: {e}",
                "namespace": self.namespace,
                "version": self.VERSION
            }
    
    def warm_cache(self, keys_to_warm: List[tuple]) -> dict:
        """
        Warm cache with pre-populated data.
        
        Args:
            keys_to_warm: List of (key, fetcher_function, ttl) tuples
            
        Returns:
            Dictionary with warming results
        """
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for key, fetcher_fn, ttl in keys_to_warm:
            try:
                # Skip if already cached
                if self.get(key) is not None:
                    results["skipped"] += 1
                    continue
                
                # Fetch and cache data
                data = fetcher_fn()
                if self.set(key, data, ttl):
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print(f"⚠️ Cache warming failed for key {key}: {e}")
                results["failed"] += 1
        
        return results
