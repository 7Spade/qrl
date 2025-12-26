"""
Redis cache module for trading bot.

Provides high-performance caching using Redis.
Redis is REQUIRED for trading bot operation.
"""

from typing import Any, List
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
            return obj.decode("utf-8")
        return super().default(obj)


class CacheClient:
    """Redis cache client - required component for trading bot."""

    # Cache key version for schema migrations
    VERSION = "v1"

    def __init__(self, config: CacheConfig, namespace: str = "qrl"):
        """
        Initialize cache client.

        Args:
            config: Cache configuration (must have valid redis_url)
            namespace: Cache key namespace for environment separation (default: "qrl")

        Raises:
            RuntimeError: If Redis connection cannot be established
        """
        self.config = config
        self.namespace = namespace
        self._redis = None

        # Initialize Redis - REQUIRED
        self._init_redis()

    def _init_redis(self) -> None:
        """Initialize Redis connection with max memory policy.

        Raises:
            RuntimeError: If Redis connection fails
        """
        try:
            import redis
        except ImportError:
            raise RuntimeError(
                "Redis library not installed. Install with: pip install redis"
            )

        try:
            self._redis = redis.from_url(
                self.config.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            self._redis.ping()

            # Set max memory policy to prevent unbounded growth
            try:
                self._redis.config_set("maxmemory-policy", "allkeys-lru")
            except Exception as e:
                print(
                    f"⚠️ Cannot set maxmemory-policy (may require admin): {e}"
                )

            print(
                f"✅ Redis connected: {self.config.redis_url.split('@')[-1]}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Redis at {self.config.redis_url}: {e}\n"
                "Redis is required for trading bot operation. "
                "Please ensure Redis is running and REDIS_URL is configured correctly."
            )

    def _ensure_connection(self) -> None:
        """
        Ensure Redis connection is available, attempt reconnection if needed.

        Raises:
            RuntimeError: If reconnection fails
        """
        try:
            self._redis.ping()
        except Exception as e:
            # Attempt reconnection
            print(f"⚠️ Redis connection lost, attempting reconnection: {e}")
            self._init_redis()

    def _make_key(self, key: str) -> str:
        """
        Generate namespaced cache key with version.

        Args:
            key: Base cache key

        Returns:
            Namespaced and versioned cache key
        """
        return f"{self.namespace}:{self.VERSION}:{key}"

    def get(self, key: str) -> Any:
        """
        Get value from cache with automatic reconnection.

        Args:
            key: Cache key (will be namespaced automatically)

        Returns:
            Cached value

        Raises:
            RuntimeError: If Redis operation fails after reconnection attempt
        """
        try:
            self._ensure_connection()
            namespaced_key = self._make_key(key)
            value = self._redis.get(namespaced_key)
            if value:
                return json.loads(value)
            return None
        except json.JSONDecodeError as e:
            print(f"⚠️ Cache JSON decode error for key {key}: {e}")
            # Delete corrupted cache entry
            self.delete(key)
            return None
        except Exception as e:
            raise RuntimeError(f"Redis get operation failed: {e}")

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Set value in cache with automatic reconnection.

        Args:
            key: Cache key (will be namespaced automatically)
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (uses config default if None)

        Raises:
            RuntimeError: If Redis operation fails
            ValueError: If value cannot be serialized
        """
        try:
            self._ensure_connection()
            ttl = ttl or self.config.cache_ttl
            namespaced_key = self._make_key(key)
            self._redis.setex(
                namespaced_key,
                timedelta(seconds=ttl),
                json.dumps(value, cls=CustomJSONEncoder),
            )
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot serialize value for key {key}: {e}")
        except Exception as e:
            raise RuntimeError(f"Redis set operation failed: {e}")

    def delete(self, key: str) -> None:
        """
        Delete key from cache with automatic reconnection.

        Args:
            key: Cache key (will be namespaced automatically)

        Raises:
            RuntimeError: If Redis operation fails
        """
        try:
            self._ensure_connection()
            namespaced_key = self._make_key(key)
            self._redis.delete(namespaced_key)
        except Exception as e:
            raise RuntimeError(f"Redis delete operation failed: {e}")

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern with automatic reconnection.

        Args:
            pattern: Pattern to match (will be namespaced automatically)
                    Examples: "ticker:*", "ohlcv:QRLUSDT:*"

        Returns:
            Number of keys deleted

        Raises:
            RuntimeError: If Redis operation fails
        """
        try:
            self._ensure_connection()
            namespaced_pattern = self._make_key(pattern)
            keys = list(self._redis.scan_iter(match=namespaced_pattern))
            if keys:
                return self._redis.delete(*keys)
            return 0
        except Exception as e:
            raise RuntimeError(f"Redis delete_pattern operation failed: {e}")

    def clear_all(self) -> None:
        """
        Clear all cache entries for this namespace with automatic reconnection.

        Only clears keys with the current namespace prefix, safe for shared Redis.

        Raises:
            RuntimeError: If Redis operation fails
        """
        try:
            self._ensure_connection()
            # Only delete keys with our namespace prefix
            pattern = f"{self.namespace}:{self.VERSION}:*"
            keys = list(self._redis.scan_iter(match=pattern))
            if keys:
                self._redis.delete(*keys)
        except Exception as e:
            raise RuntimeError(f"Redis clear_all operation failed: {e}")

    def clear_symbol(self, symbol: str) -> int:
        """
        Clear all cache entries for a specific symbol.

        Args:
            symbol: Trading symbol (e.g., "QRL/USDT")

        Returns:
            Number of keys deleted
        """
        # Normalize symbol for pattern matching (replace / with escaped version)
        symbol_pattern = symbol.replace("/", "?")
        return self.delete_pattern(f"*{symbol_pattern}*")

    def get_stats(self) -> dict:
        """
        Get cache statistics with automatic reconnection.

        Returns:
            Dictionary with cache stats

        Raises:
            RuntimeError: If Redis operation fails
        """
        try:
            self._ensure_connection()
            info = self._redis.info()

            # Count keys in our namespace
            pattern = f"{self.namespace}:{self.VERSION}:*"
            namespace_keys = len(
                list(self._redis.scan_iter(match=pattern, count=100))
            )

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
            raise RuntimeError(f"Redis get_stats operation failed: {e}")

    def warm_cache(self, keys_to_warm: List[tuple]) -> dict:
        """
        Warm cache with pre-populated data.

        Args:
            keys_to_warm: List of (key, fetcher_function, ttl) tuples

        Returns:
            Dictionary with warming results

        Raises:
            RuntimeError: If critical Redis operations fail
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
                self.set(key, data, ttl)
                results["success"] += 1
            except Exception as e:
                print(f"⚠️ Cache warming failed for key {key}: {e}")
                results["failed"] += 1

        return results
