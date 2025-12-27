"""
Exchange integration module for MEXC cryptocurrency exchange.

Provides abstraction layer for exchange API interactions with
error handling, rate limiting, automatic retry, and Redis caching.
"""

from typing import Dict, Any, List, Optional, Callable, TYPE_CHECKING
import ccxt
import time
from functools import wraps
from src.core.config import ExchangeConfig, CacheConfig
from src.data.cache import CacheClient

if TYPE_CHECKING:
    from src.data.state import StateManager


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
                        wait_time = delay * (2**attempt)
                        msg = (
                            f"⚠️ Network error (attempt {attempt + 1}/"
                            f"{max_attempts}): {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        print(msg)
                        time.sleep(wait_time)
                    else:
                        msg = (
                            f"❌ Network error after {max_attempts} "
                            f"attempts: {e}"
                        )
                        print(msg)
                except ccxt.ExchangeError as e:
                    # Don't retry on exchange errors
                    # (invalid params, insufficient funds, etc.)
                    raise e

            # If we get here, all attempts failed
            raise last_exception

        return wrapper

    return decorator


class ExchangeClient:
    """
    MEXC exchange client wrapper with Redis caching and persistent storage.
    """

    def __init__(
        self,
        config: ExchangeConfig,
        cache_config: CacheConfig,
        state_manager: Optional["StateManager"] = None,
    ):
        """
        Initialize exchange client.

        Args:
            config: Exchange configuration
            cache_config: Cache configuration (REQUIRED)
            state_manager: Optional StateManager for persistent OHLCV storage

        Raises:
            RuntimeError: If cache initialization fails
        """
        self.config = config
        self.cache_config = cache_config
        self._exchange: Optional[ccxt.Exchange] = None
        self._state_manager = state_manager

        # Initialize cache - REQUIRED
        self._cache = CacheClient(
            cache_config, namespace=cache_config.namespace
        )

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
        Generate human-readable cache key for API call.

        Args:
            method: API method name
            args: Method arguments

        Returns:
            Cache key string (e.g., "ohlcv:QRL/USDT:1d:120")
        """
        # Use readable cache keys instead of MD5 hash for better debugging
        return f"{method}:{':'.join(str(arg) for arg in args)}"

    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_ticker(
        self, symbol: str, use_cache: bool = True
    ) -> Dict[str, Any]:
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
            RuntimeError: If Redis operation fails
        """
        cache_key = self._get_cache_key("ticker", symbol)

        # Try cache first if enabled
        if use_cache:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data

        # Fetch from API
        data = self.exchange.fetch_ticker(symbol)

        # Store in cache with configured TTL for ticker data
        self._cache.set(
            cache_key, data, ttl=self.cache_config.cache_ttl_ticker
        )

        return data

    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 120,
        use_cache: bool = True,
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
            RuntimeError: If Redis operation fails
        """
        cache_key = self._get_cache_key("ohlcv", symbol, timeframe, limit)

        # Try cache first if enabled
        if use_cache:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                print(f"📦 Using cached OHLCV data for {symbol} ({len(cached_data)} candles)")
                return cached_data

        # Fetch from API
        print(f"🔄 Fetching OHLCV from MEXC: {symbol}, timeframe={timeframe}, limit={limit}")
        data = self.exchange.fetch_ohlcv(symbol, timeframe, limit)
        
        if not data:
            print(f"⚠️ MEXC returned empty OHLCV data for {symbol} with timeframe {timeframe}")
        else:
            print(f"✅ Fetched {len(data)} candles from MEXC")

        # Store in cache with configured TTL for OHLCV data
        self._cache.set(cache_key, data, ttl=self.cache_config.cache_ttl_ohlcv)

        return data

    def fetch_ohlcv_with_fallback(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 120,
        use_cache: bool = True,
    ) -> List[List[Any]]:
        """
        Fetch OHLCV data with automatic fallback to alternative timeframes.
        
        If the requested timeframe returns no data, automatically tries
        alternative timeframes in order: 1h, 4h, 15m.
        
        Args:
            symbol: Trading pair symbol
            timeframe: Primary candlestick timeframe to try first
            limit: Number of candles to fetch
            use_cache: Whether to use cache (default: True)
        
        Returns:
            List of OHLCV candles
            
        Raises:
            ccxt.NetworkError: Network connection failed after retries
            ccxt.ExchangeError: Exchange API error
        """
        # Try primary timeframe first
        print(f"🎯 Attempting to fetch {symbol} data with timeframe: {timeframe}")
        data = self.fetch_ohlcv(symbol, timeframe, limit, use_cache)
        
        if data and len(data) > 0:
            return data
        
        # Define fallback timeframes (most common to least common)
        fallback_timeframes = ["1h", "4h", "15m", "5m"]
        
        # Remove the original timeframe from fallbacks if it's there
        if timeframe in fallback_timeframes:
            fallback_timeframes.remove(timeframe)
        
        print(f"⚠️ Primary timeframe '{timeframe}' returned no data")
        print(f"🔄 Trying fallback timeframes: {', '.join(fallback_timeframes)}")
        
        # Try each fallback timeframe
        for tf in fallback_timeframes:
            print(f"   → Trying {tf}...")
            data = self.fetch_ohlcv(symbol, tf, limit, use_cache)
            
            if data and len(data) > 0:
                print(f"✅ Successfully fetched data with timeframe: {tf}")
                print(f"💡 IMPORTANT: Update your .env file with: TIMEFRAME={tf}")
                return data
        
        # If all timeframes failed, try alternative symbol formats
        print(f"⚠️ All timeframes failed for {symbol}")
        print(f"🔄 Trying alternative symbol formats...")
        
        # Try common symbol format variations
        symbol_variations = []
        if "/" in symbol:
            # Try without slash (QRL/USDT -> QRLUSDT)
            symbol_variations.append(symbol.replace("/", ""))
        else:
            # Try with slash (QRLUSDT -> QRL/USDT)
            if "USDT" in symbol:
                base = symbol.replace("USDT", "")
                symbol_variations.append(f"{base}/USDT")
        
        for alt_symbol in symbol_variations:
            print(f"   → Trying symbol format: {alt_symbol}")
            try:
                data = self.fetch_ohlcv(alt_symbol, timeframe, limit, use_cache=False)
                if data and len(data) > 0:
                    print(f"✅ Successfully fetched data with symbol: {alt_symbol}")
                    print(f"💡 IMPORTANT: Update your .env file with: SYMBOL={alt_symbol}")
                    return data
            except Exception as e:
                print(f"   ✗ Failed with {alt_symbol}: {e}")
        
        # All attempts failed
        print(f"❌ Failed to fetch OHLCV data for {symbol} with any timeframe or format")
        print(f"📋 Tried timeframes: {timeframe}, {', '.join(fallback_timeframes)}")
        print(f"📋 Tried symbol formats: {symbol}, {', '.join(symbol_variations)}")
        print(f"💡 Troubleshooting suggestions:")
        print(f"   1. Verify symbol exists on MEXC: https://www.mexc.com/exchange")
        print(f"   2. Check exact symbol format in MEXC API documentation")
        print(f"   3. Verify the pair has active trading (not delisted)")
        print(f"   4. Try manually on MEXC website to confirm it exists")
        
        return []

    def create_limit_buy_order(
        self, symbol: str, amount: float, price: float
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
    def fetch_balance(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch account balance with Redis caching and auto-retry.

        Args:
            use_cache: Whether to use cache (default: True)

        Returns:
            Balance information

        Raises:
            ccxt.NetworkError: Network connection failed after retries
            ccxt.ExchangeError: Exchange API error
            RuntimeError: If Redis operation fails
        """
        cache_key = self._get_cache_key("balance")

        # Try cache first if enabled
        if use_cache:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data

        # Fetch from API
        data = self.exchange.fetch_balance()

        # Store in cache with configured TTL for balance data
        self._cache.set(
            cache_key, data, ttl=self.cache_config.cache_ttl_balance
        )

        return data

    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_deals(
        self, symbol: str, limit: int = 20, use_cache: bool = True
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
            RuntimeError: If Redis operation fails
        """
        cache_key = self._get_cache_key("deals", symbol, limit)

        # Try cache first if enabled
        if use_cache:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data

        # Fetch from API
        data = self.exchange.fetch_trades(symbol, limit=limit)

        # Store in cache with configured TTL for deals data
        self._cache.set(cache_key, data, ttl=self.cache_config.cache_ttl_deals)

        return data

    @retry_on_network_error(max_attempts=3, delay=1.0)
    def fetch_order_book(
        self, symbol: str, limit: int = 20, use_cache: bool = True
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
            RuntimeError: If Redis operation fails
        """
        cache_key = self._get_cache_key("orderbook", symbol, limit)

        # Try cache first if enabled
        if use_cache:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                return cached_data

        # Fetch from API
        data = self.exchange.fetch_order_book(symbol, limit=limit)

        # Store in cache with configured TTL for order book data
        self._cache.set(
            cache_key, data, ttl=self.cache_config.cache_ttl_orderbook
        )

        return data

    def get_cache_stats(self) -> dict:
        """
        Get Redis cache statistics.

        Returns:
            Dictionary with cache stats

        Raises:
            RuntimeError: If Redis operation fails
        """
        return self._cache.get_stats()

    def invalidate_cache(self, symbol: str | None = None) -> dict:
        """
        Invalidate cache entries.

        Args:
            symbol: Optional symbol to invalidate. If None, clears all cache.

        Returns:
            Dictionary with invalidation results

        Raises:
            RuntimeError: If Redis operation fails
        """
        if symbol:
            count = self._cache.clear_symbol(symbol)
            return {
                "symbol": symbol,
                "keys_deleted": count,
                "status": "success",
            }
        else:
            self._cache.clear_all()
            return {"all_cleared": True, "status": "success"}
