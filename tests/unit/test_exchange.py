"""
Unit tests for exchange client.

Tests caching behavior and API integration.
"""

from unittest.mock import Mock, patch
from src.data.exchange import ExchangeClient
from src.core.config import ExchangeConfig, CacheConfig


class TestExchangeClient:
    """Test cases for ExchangeClient."""

    def test_fetch_balance_with_cache(self):
        """Test that fetch_balance uses Redis caching."""
        # Skip test if redis module not available
        try:
            import redis  # noqa: F401
        except ImportError:
            import pytest

            pytest.skip("Redis module not installed")

        exchange_config = ExchangeConfig(
            api_key="test_key", api_secret="test_secret"
        )
        cache_config = CacheConfig(redis_url="redis://localhost:6379")

        with patch("redis.from_url") as mock_from_url:
            # Setup mock Redis client
            mock_redis_instance = Mock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = None
            mock_redis_instance.setex.return_value = True
            mock_from_url.return_value = mock_redis_instance

            with patch("ccxt.mexc") as mock_mexc:
                # Setup mock exchange
                mock_exchange_instance = Mock()
                mock_balance = {
                    "USDT": {"free": 1000.0, "used": 0.0, "total": 1000.0}
                }
                mock_exchange_instance.fetch_balance.return_value = (
                    mock_balance
                )
                mock_mexc.return_value = mock_exchange_instance

                # Create client and fetch balance
                client = ExchangeClient(exchange_config, cache_config)
                result = client.fetch_balance(use_cache=True)

                # Verify balance was fetched
                assert result == mock_balance
                mock_exchange_instance.fetch_balance.assert_called_once()

                # Verify cache was set
                assert mock_redis_instance.setex.called

    def test_fetch_balance_cache_bypass(self):
        """Test that fetch_balance can bypass cache."""
        # Skip test if redis module not available
        try:
            import redis  # noqa: F401
        except ImportError:
            import pytest

            pytest.skip("Redis module not installed")

        exchange_config = ExchangeConfig(
            api_key="test_key", api_secret="test_secret"
        )
        cache_config = CacheConfig(redis_url="redis://localhost:6379")

        with patch("redis.from_url") as mock_from_url:
            # Setup mock Redis client
            mock_redis_instance = Mock()
            mock_redis_instance.ping.return_value = True
            mock_from_url.return_value = mock_redis_instance

            with patch("ccxt.mexc") as mock_mexc:
                # Setup mock exchange
                mock_exchange_instance = Mock()
                mock_balance = {
                    "USDT": {"free": 1000.0, "used": 0.0, "total": 1000.0}
                }
                mock_exchange_instance.fetch_balance.return_value = (
                    mock_balance
                )
                mock_mexc.return_value = mock_exchange_instance

                # Create client and fetch balance with cache bypass
                client = ExchangeClient(exchange_config, cache_config)
                result = client.fetch_balance(use_cache=False)

                # Verify balance was fetched
                assert result == mock_balance

                # Verify cache.get was NOT called (bypassed)
                mock_redis_instance.get.assert_not_called()
