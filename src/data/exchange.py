"""
Exchange integration module for MEXC cryptocurrency exchange.

Provides abstraction layer for exchange API interactions with
error handling, rate limiting, automatic retry, and Redis caching.
"""
from typing import Dict, Any, List, Optional, Callable
import ccxt
import hashlib
import time
from functools import wraps
from src.core.config import ExchangeConfig, CacheConfig
from src.data.cache import CacheClient


def retry_on_network_error(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator for retrying operations on network errors.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds (exponential backoff)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ccxt.NetworkError as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt)
                        print(f"⚠️ Network error (attempt {attempt + 1}/{max_attempts}): {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Network error after {max_attempts} attempts: {e}")
                except ccxt.ExchangeError as e:
                    # Don't retry on exchange errors (invalid params, insufficient funds, etc.)
                    raise e
            
            # If we get here, all attempts failed
            raise last_exception
        return wrapper
    return decorator


class ExchangeClient:
    """MEXC exchange client wrapper with Redis caching and retry support."""
    
    def __init__(self, config: ExchangeConfig, cache_config: Optional[CacheConfig] = None):
        """
        Initialize exchange client.
        
        Args:
            config: Exchange configuration
            cache_config: Optional cache configuration for Redis
        """
        self.config = config
        self._exchange: Optional[ccxt.Exchange] = None
        self._cache: Optional[CacheClient] = None
        
        # Initialize cache if provided
        if cache_config:
            self._cache = CacheClient(cache_config)
    
    @property
    def exchange(self) -> ccxt.Exchange:
        """Get or create exchange instance."""
        if self._exchange is None:
            exchange_config: Dict[str, Any] = {
                "apiKey": self.config.api_key,
                "secret": self.config.api_secret,
                "enableRateLimit": self.config.enable_rate_limit,
            }
            
            if self.config.subaccount:
                exchange_config["options"] = {
                    "broker": self.config.subaccount,
                }
            
            self._exchange = ccxt.mexc(exchange_config)
        
        return self._exchange
    
    def _get_cache_key(self, method: str, *args) -> str:
        """
        Generate cache key for API call.
        
        Args:
            method: API method name
            args: Method arguments
            
        Returns:
            Cache key string
        """
        key_data = f"{method}:{':'.join(str(arg) for arg in args)}"
        return f"mexc:{hashlib.md5(key_data.encode()).hexdigest()[:16]}"
    
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_ticker(self, symbol: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch current ticker data for symbol with Redis caching and auto-retry.
        
        Args:
            symbol: Trading pair symbol
            use_cache: Whether to use cache (default: True)
            
        Returns:
            Ticker data dictionary
            
        Raises:
            ccxt.NetworkError: Network connection failed after retries
            ccxt.ExchangeError: Exchange API error
        """
        cache_key = self._get_cache_key("ticker", symbol)
        
        # Try cache first if enabled
        if use_cache and self._cache and self._cache.enabled:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch from API
        data = self.exchange.fetch_ticker(symbol)
        
        # Store in cache (5 second TTL for ticker data)
        if self._cache and self._cache.enabled:
            self._cache.set(cache_key, data, ttl=5)
        
        return data
    
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 120,
        use_cache: bool = True
    ) -> List[List[Any]]:
        """
        Fetch OHLCV candlestick data with Redis caching and auto-retry.
        
        Args:
            symbol: Trading pair symbol
            timeframe: Candlestick timeframe
            limit: Number of candles to fetch
            use_cache: Whether to use cache (default: True)
            
        Returns:
            List of OHLCV candles
            
        Raises:
            ccxt.NetworkError: Network connection failed after retries
            ccxt.ExchangeError: Exchange API error
        """
        cache_key = self._get_cache_key("ohlcv", symbol, timeframe, limit)
        
        # Try cache first if enabled
        if use_cache and self._cache and self._cache.enabled:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch from API
        data = self.exchange.fetch_ohlcv(symbol, timeframe, limit)
        
        # Store in cache (60 second TTL for OHLCV data)
        if self._cache and self._cache.enabled:
            self._cache.set(cache_key, data, ttl=60)
        
        return data
    
    def create_limit_buy_order(
        self,
        symbol: str,
        amount: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Place a limit buy order.
        
        Args:
            symbol: Trading pair symbol
            amount: Amount to buy
            price: Limit price
            
        Returns:
            Order details
            
        Raises:
            ccxt.InsufficientFunds: Insufficient account balance
            ccxt.InvalidOrder: Invalid order parameters
        """
        return self.exchange.create_limit_buy_order(symbol, amount, price)
    
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_balance(self) -> Dict[str, Any]:
        """
        Fetch account balance with auto-retry.
        
        Returns:
            Balance information
            
        Raises:
            ccxt.NetworkError: Network connection failed after retries
            ccxt.ExchangeError: Exchange API error
        """
        return self.exchange.fetch_balance()
    
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_deals(
        self,
        symbol: str,
        limit: int = 20,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch latest deals/trades for symbol with Redis caching and auto-retry.
        
        Used for tick/trade price and volume analysis, VWAP calculation.
        
        Args:
            symbol: Trading pair symbol
            limit: Number of deals to fetch
            use_cache: Whether to use cache (default: True)
            
        Returns:
            List of trade records
            
        Raises:
            ccxt.NetworkError: Network connection failed after retries
            ccxt.ExchangeError: Exchange API error
        """
        cache_key = self._get_cache_key("deals", symbol, limit)
        
        # Try cache first if enabled
        if use_cache and self._cache and self._cache.enabled:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch from API
        data = self.exchange.fetch_trades(symbol, limit=limit)
        
        # Store in cache (10 second TTL for deals data)
        if self._cache and self._cache.enabled:
            self._cache.set(cache_key, data, ttl=10)
        
        return data
    
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_order_book(
        self,
        symbol: str,
        limit: int = 20,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch market depth (order book) with Redis caching and auto-retry.
        
        Used for liquidity estimation, support/resistance, VWAP order models.
        
        Args:
            symbol: Trading pair symbol
            limit: Depth limit (number of price levels)
            use_cache: Whether to use cache (default: True)
            
        Returns:
            Order book data with bids and asks
            
        Raises:
            ccxt.NetworkError: Network connection failed after retries
            ccxt.ExchangeError: Exchange API error
        """
        cache_key = self._get_cache_key("orderbook", symbol, limit)
        
        # Try cache first if enabled
        if use_cache and self._cache and self._cache.enabled:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch from API
        data = self.exchange.fetch_order_book(symbol, limit=limit)
        
        # Store in cache (5 second TTL for order book data)
        if self._cache and self._cache.enabled:
            self._cache.set(cache_key, data, ttl=5)
        
        return data
    
    def get_cache_stats(self) -> dict:
        """
        Get Redis cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if self._cache:
            return self._cache.get_stats()
        return {"enabled": False, "status": "not configured"}
