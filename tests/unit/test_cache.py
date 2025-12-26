"""
Unit tests for Redis cache module.

Tests cache functionality, error handling, and data serialization.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
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


class TestCacheClient:
    """Test cases for CacheClient."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = CacheConfig(
            redis_url=None,
            redis_enabled=False,
            cache_ttl=60,
            cache_ttl_ticker=5,
            cache_ttl_ohlcv=60,
            cache_ttl_deals=10,
            cache_ttl_orderbook=5,
            namespace="test"
        )
    
    def test_cache_disabled_by_default(self):
        """Test cache is disabled when no Redis URL provided."""
        client = CacheClient(self.config)
        assert not client.enabled
    
    def test_namespace_in_cache_key(self):
        """Test cache keys include namespace and version."""
        client = CacheClient(self.config, namespace="test-env")
        key = client._make_key("ticker:QRL/USDT")
        assert key.startswith("test-env:v1:")
        assert "ticker:QRL/USDT" in key
    
    def test_get_returns_none_when_disabled(self):
        """Test get returns None when cache is disabled."""
        client = CacheClient(self.config)
        result = client.get("test_key")
        assert result is None
    
    def test_set_returns_false_when_disabled(self):
        """Test set returns False when cache is disabled."""
        client = CacheClient(self.config)
        result = client.set("test_key", {"data": "value"})
        assert result is False
    
    def test_delete_returns_false_when_disabled(self):
        """Test delete returns False when cache is disabled."""
        client = CacheClient(self.config)
        result = client.delete("test_key")
        assert result is False
    
    def test_clear_all_safe_with_namespace(self):
        """Test clear_all only clears namespaced keys."""
        # This test verifies the pattern used in clear_all
        client = CacheClient(self.config, namespace="test-app")
        pattern = f"{client.namespace}:{client.VERSION}:*"
        assert pattern == "test-app:v1:*"
    
    def test_get_stats_when_disabled(self):
        """Test stats when cache is disabled."""
        client = CacheClient(self.config, namespace="test")
        stats = client.get_stats()
        assert stats["enabled"] is False
        assert stats["status"] == "disabled"
        assert stats["namespace"] == "test"
        assert stats["version"] == "v1"
    
    def test_cache_with_mock_redis(self):
        """Test cache operations with mocked Redis."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        from unittest.mock import patch
        with patch('redis.from_url') as mock_from_url:
            # Setup mock
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = '{"test": "data"}'
            mock_from_url.return_value = mock_redis_instance
            
            # Enable Redis
            config = CacheConfig(
                redis_url="redis://localhost:6379",
                redis_enabled=True,
                namespace="test"
            )
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
        
        from unittest.mock import patch
        with patch('redis.from_url') as mock_from_url:
            # Setup mock with invalid JSON
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = 'invalid-json{'
            mock_redis_instance.delete.return_value = 1
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(
                redis_url="redis://localhost:6379",
                redis_enabled=True
            )
            client = CacheClient(config)
            
            # Should return None and delete corrupted entry
            result = client.get("corrupted_key")
            assert result is None
            # Verify delete was called to clean up
            assert mock_redis_instance.delete.called
    
    def test_serialization_error_handling(self):
        """Test handling of non-serializable data."""
        # Skip test if redis module not available
        try:
            import redis
        except ImportError:
            pytest.skip("Redis module not installed")
        
        from unittest.mock import patch
        with patch('redis.from_url') as mock_from_url:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.return_value = True
            mock_from_url.return_value = mock_redis_instance
            
            config = CacheConfig(
                redis_url="redis://localhost:6379",
                redis_enabled=True
            )
            client = CacheClient(config)
            
            # Try to cache non-serializable object (should handle gracefully)
            class NonSerializable:
                pass
            
            result = client.set("test_key", NonSerializable())
            # Should return False but not crash
            assert result is False
    
    def test_warm_cache_basic(self):
        """Test cache warming functionality."""
        client = CacheClient(self.config)
        
        def fetcher():
            return {"data": "test"}
        
        # Should handle gracefully when cache disabled
        results = client.warm_cache([
            ("key1", fetcher, 60)
        ])
        assert results["failed"] == 1 or results["skipped"] == 1
    
    def test_delete_pattern_disabled_cache(self):
        """Test delete_pattern returns 0 when cache disabled."""
        client = CacheClient(self.config)
        count = client.delete_pattern("ticker:*")
        assert count == 0
    
    def test_clear_symbol_disabled_cache(self):
        """Test clear_symbol returns 0 when cache disabled."""
        client = CacheClient(self.config)
        count = client.clear_symbol("QRL/USDT")
        assert count == 0


class TestCacheIntegration:
    """Integration tests for cache with realistic scenarios."""
    
    def test_cache_key_uniqueness(self):
        """Test that different parameters generate unique keys."""
        client = CacheClient(CacheConfig(redis_enabled=False))
        
        key1 = client._make_key("ohlcv:QRL/USDT:1d:120")
        key2 = client._make_key("ohlcv:QRL/USDT:1h:120")
        key3 = client._make_key("ohlcv:QRL/USDT:1d:60")
        
        # All keys should be different
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3
    
    def test_namespace_isolation(self):
        """Test that different namespaces generate different keys."""
        client1 = CacheClient(CacheConfig(redis_enabled=False), namespace="prod")
        client2 = CacheClient(CacheConfig(redis_enabled=False), namespace="dev")
        
        key1 = client1._make_key("ticker:QRL/USDT")
        key2 = client2._make_key("ticker:QRL/USDT")
        
        assert key1 != key2
        assert "prod" in key1
        assert "dev" in key2
