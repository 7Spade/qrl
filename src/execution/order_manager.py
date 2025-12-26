"""
Order execution and management module.

Handles order placement, tracking, and execution status monitoring.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import ccxt
from src.data.exchange import ExchangeClient


@dataclass
class OrderResult:
    """Result of an order execution."""
    
    success: bool
    order_id: Optional[str] = None
    price: Optional[float] = None
    amount: Optional[float] = None
    cost: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        """Initialize metadata if None."""
        if self.metadata is None:
            self.metadata = {}


class OrderManager:
    """
    Manages order execution and tracking.
    
    Provides abstraction layer for order placement with
    error handling and result tracking.
    """
    
    def __init__(self, exchange_client: ExchangeClient):
        """
        Initialize order manager.
        
        Args:
            exchange_client: Exchange client instance
        """
        self.exchange = exchange_client
    
    def place_limit_buy(
        self,
        symbol: str,
        amount: float,
        price: float
    ) -> OrderResult:
        """
        Place a limit buy order.
        
        Args:
            symbol: Trading pair symbol
            amount: Amount to buy
            price: Limit price
        
        Returns:
            OrderResult with execution details
        """
        try:
            order = self.exchange.create_limit_buy_order(
                symbol,
                amount,
                price
            )
            
            return OrderResult(
                success=True,
                order_id=order.get("id"),
                price=price,
                amount=amount,
                cost=price * amount,
                metadata={
                    "symbol": symbol,
                    "timestamp": datetime.utcnow().isoformat(),
                    "order_data": order,
                }
            )
        
        except ccxt.InsufficientFunds as e:
            return OrderResult(
                success=False,
                error=f"Insufficient funds: {str(e)}"
            )
        
        except ccxt.InvalidOrder as e:
            return OrderResult(
                success=False,
                error=f"Invalid order: {str(e)}"
            )
        
        except ccxt.NetworkError as e:
            return OrderResult(
                success=False,
                error=f"Network error: {str(e)}"
            )
        
        except Exception as e:
            return OrderResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def calculate_order_params(
        self,
        ticker_price: float,
        order_size_usdt: float,
        price_offset: float = 0.98
    ) -> Dict[str, float]:
        """
        Calculate order parameters from market price and size.
        
        Args:
            ticker_price: Current market price
            order_size_usdt: Order size in USDT
            price_offset: Price offset multiplier (0.98 = 2% below)
        
        Returns:
            Dictionary with 'price' and 'amount' keys
        """
        limit_price = ticker_price * price_offset
        amount = order_size_usdt / limit_price
        
        return {
            "price": limit_price,
            "amount": amount,
        }
