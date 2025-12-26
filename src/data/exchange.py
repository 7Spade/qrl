"""
Exchange integration module for MEXC cryptocurrency exchange.

Provides abstraction layer for exchange API interactions with
error handling and rate limiting.
"""
from typing import Dict, Any, List, Optional
import ccxt
from src.core.config import ExchangeConfig


class ExchangeClient:
    """MEXC exchange client wrapper."""
    
    def __init__(self, config: ExchangeConfig):
        """
        Initialize exchange client.
        
        Args:
            config: Exchange configuration
        """
        self.config = config
        self._exchange: Optional[ccxt.Exchange] = None
    
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
    
    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current ticker data for symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Ticker data dictionary
            
        Raises:
            ccxt.NetworkError: Network connection failed
            ccxt.ExchangeError: Exchange API error
        """
        return self.exchange.fetch_ticker(symbol)
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 120
    ) -> List[List[Any]]:
        """
        Fetch OHLCV candlestick data.
        
        Args:
            symbol: Trading pair symbol
            timeframe: Candlestick timeframe
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCV candles
            
        Raises:
            ccxt.NetworkError: Network connection failed
            ccxt.ExchangeError: Exchange API error
        """
        return self.exchange.fetch_ohlcv(symbol, timeframe, limit)
    
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
    
    def fetch_balance(self) -> Dict[str, Any]:
        """
        Fetch account balance.
        
        Returns:
            Balance information
            
        Raises:
            ccxt.NetworkError: Network connection failed
            ccxt.ExchangeError: Exchange API error
        """
        return self.exchange.fetch_balance()
