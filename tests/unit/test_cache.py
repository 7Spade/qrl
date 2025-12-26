"""
Unit tests for Redis cache module.

Tests cache functionality, error handling, and data serialization.
Redis is REQUIRED for trading bot operation.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from src.data.cache import CacheClient, CustomJSONEncoder
from src.core.config import CacheConfig


class TestCustomJSONEncoder:
    """Test custom JSON encoder for trading data types."""
    
    def test_encode_decimal(self):
        """Test Decimal serialization."""
        import json
        data = {"price": Decimal("123.45")}
        result = json.dumps(data, cls=CustomJSONEncoder)
        assert '"price": 123.45' in result
    
    def test_encode_datetime(self):
        """Test datetime serialization."""
        import json
        dt = datetime(2024, 1, 1, 12, 0, 0)
        data = {"timestamp": dt}
        result = json.dumps(data, cls=CustomJSONEncoder)
        assert "2024-01-01T12:00:00" in result
    
    def test_encode_bytes(self):
        """Test bytes serialization."""
        import json
        data = {"binary": b"test"}
        result = json.dumps(data, cls=CustomJSONEncoder)
        assert '"binary": "test"' in result


class TestCacheConfig:
    """Test cache configuration."""
    
    def test_config_requires_redis_url(self):
        """Test that CacheConfig requires redis_url."""
        with pytest.raises(Exception):  # Pydantic validation error
            CacheConfig()
    
    def test_config_from_env_without_url_fails(self):
        """Test that from_env raises error without REDIS_URL."""
        import os
        # Ensure REDIS_URL is not set
        old_url = os.environ.pop('REDIS_URL', None)
        try:
            with pytest.raises(ValueError, match="REDIS_URL environment variable is required"):
                CacheConfig.from_env()
        finally:
            if old_url:
                os.environ['REDIS_URL'] = old_url


class TestCacheClient:
    """Test cases for CacheClient - Redis required."""
    
    def test_initialization_requires_redis(self):
        """Test that CacheClient init fails without valid Redis connection."""
        # Skip test if redis module not available
        try:
            import redis  # noqa: F401
        except ImportError:
            pytest.skip("Redis module not installed")
        
        config = CacheConfig(redis_url="redis://invalid-host:9999")
        
        with pytest.raises(RuntimeError, match="Failed to connect to Redis"):
            CacheClient(config)
    
    def test_namespace_in_cache_key(self):
        """Test cache keys include namespace and version."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client = CacheClient(config, namespace="test-env")
            key = client._make_key("ticker:QRL/USDT")
            assert key.startswith("test-env:v1:")
            assert "ticker:QRL/USDT" in key
    
    def test_cache_with_mock_redis(self):
        """Test cache operations with mocked Redis."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            # Setup mock
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = '{"test": "data"}'
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client = CacheClient(config)
            
            # Test get
            result = client.get("test_key")
            assert result == {"test": "data"}
            mock_redis_instance.get.assert_called_once()
    
    def test_json_decode_error_handling(self):
        """Test handling of corrupted cache data."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            # Setup mock with invalid JSON
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = 'invalid-json{'
            mock_redis_instance.delete.return_value = 1
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client = CacheClient(config)
            
            # Should return None and delete corrupted entry
            result = client.get("corrupted_key")
            assert result is None
            # Verify delete was called to clean up
            assert mock_redis_instance.delete.called
    
    def test_set_with_ttl(self):
        """Test setting cache with custom TTL."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client = CacheClient(config)
            
            # Set with custom TTL
            client.set("test_key", {"data": "value"}, ttl=30)
            
            # Verify setex was called
            assert mock_redis_instance.setex.called
    
    def test_serialization_error_raises(self):
        """Test that non-serializable data raises ValueError."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client = CacheClient(config)
            
            # Try to cache non-serializable object
            class NonSerializable:
                pass
            
            with pytest.raises(ValueError, match="Cannot serialize"):
                client.set("test_key", NonSerializable())
    
    def test_get_stats(self):
        """Test getting cache statistics."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.info.return_value = {
                "used_memory_human": "1.5M",
                "used_memory_peak_human": "2M",
                "maxmemory_policy": "allkeys-lru",
                "uptime_in_seconds": 3600,
                "evicted_keys": 0
            }
            mock_redis_instance.dbsize.return_value = 100
            mock_redis_instance.scan_iter.return_value = iter([])
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client = CacheClient(config)
            
            stats = client.get_stats()
            assert stats["status"] == "connected"
            assert stats["memory_used"] == "1.5M"
            assert stats["maxmemory_policy"] == "allkeys-lru"


class TestCacheIntegration:
    """Integration tests for cache with realistic scenarios."""
    
    def test_cache_key_uniqueness(self):
        """Test that different parameters generate unique keys."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client = CacheClient(config)
            
            key1 = client._make_key("ohlcv:QRL/USDT:1d:120")
            key2 = client._make_key("ohlcv:QRL/USDT:1h:120")
            key3 = client._make_key("ohlcv:QRL/USDT:1d:60")
            
            # All keys should be different
            assert key1 != key2
            assert key1 != key3
            assert key2 != key3
    
    def test_namespace_isolation(self):
        """Test that different namespaces generate different keys."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        with patch('redis.from_url') as mock_from_url:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(redis_url="redis://localhost:6379")
            client1 = CacheClient(config, namespace="prod")
            client2 = CacheClient(config, namespace="dev")
            
            key1 = client1._make_key("ticker:QRL/USDT")
            key2 = client2._make_key("ticker:QRL/USDT")
            
            assert key1 != key2
            assert "prod" in key1
            assert "dev" in key2
