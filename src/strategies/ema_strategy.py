"""
EMA-based accumulation strategy.

Implements a conservative accumulation strategy using Exponential
Moving Averages to identify favorable entry points.
"""
from typing import List, Any
import pandas as pd
from ta.trend import EMAIndicator
from src.strategies.base import BaseStrategy, StrategySignal


class EMAAccumulationStrategy(BaseStrategy):
    """
    EMA20/60 accumulation strategy.
    
    Buy conditions:
    1. Price near support (within 2% of EMA60)
    2. Positive momentum (EMA20 >= EMA60)
    """
    
    def __init__(
        self,
        ema_short: int = 20,
        ema_long: int = 60,
        support_threshold: float = 1.02
    ):
        """
        Initialize EMA strategy.
        
        Args:
            ema_short: Short EMA period (default: 20)
            ema_long: Long EMA period (default: 60)
            support_threshold: Price/EMA60 threshold (default: 1.02)
        """
        super().__init__(name="EMA Accumulation")
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.support_threshold = support_threshold
    
    def get_required_candles(self) -> int:
        """Return minimum candles needed (max of EMA periods)."""
        return max(self.ema_short, self.ema_long)
    
    def analyze(self, ohlcv: List[List[Any]]) -> StrategySignal:
        """
        Analyze market data using EMA indicators.
        
        Args:
            ohlcv: OHLCV candlestick data
        
        Returns:
            StrategySignal with buy recommendation
        
        Raises:
            ValueError: If data is invalid or insufficient
        """
        self.validate_data(ohlcv)
        
        df = pd.DataFrame(
            ohlcv,
            columns=["ts", "open", "high", "low", "close", "vol"]
        )
        
        df["ema_short"] = EMAIndicator(
            df["close"],
            self.ema_short
        ).ema_indicator()
        
        df["ema_long"] = EMAIndicator(
            df["close"],
            self.ema_long
        ).ema_indicator()
        
        latest = df.iloc[-1]
        
        near_support = bool(
            latest["close"] <= latest["ema_long"] * self.support_threshold
        )
        positive_momentum = bool(latest["ema_short"] >= latest["ema_long"])
        
        should_buy = near_support and positive_momentum
        
        return StrategySignal(
            should_buy=should_buy,
            should_sell=False,
            confidence=1.0 if should_buy else 0.0,
            metadata={
                "price": float(latest["close"]),
                "ema_short": float(latest["ema_short"]),
                "ema_long": float(latest["ema_long"]),
                "near_support": near_support,
                "positive_momentum": positive_momentum,
            }
        )
