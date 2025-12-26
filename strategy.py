"""
Trading strategy module implementing EMA-based buy signals.

This module analyzes historical price data using Exponential Moving Averages
to identify favorable entry points for accumulating QRL tokens.
"""
from typing import List, Any
import pandas as pd
from ta.trend import EMAIndicator


def should_buy(ohlcv: List[List[Any]]) -> bool:
    """
    Determine if conditions are favorable for buying based on EMA indicators.

    Buy signal conditions:
    1. Current price is within 2% of the 60-period EMA (near support)
    2. 20-period EMA is above or equal to 60-period EMA (positive momentum)

    Args:
        ohlcv: List of OHLCV candles
               [timestamp, open, high, low, close, volume]

    Returns:
        bool: True if buy conditions are met, False otherwise

    Raises:
        ValueError: When ohlcv data is empty or invalid
    """
    if not ohlcv or len(ohlcv) < 60:
        raise ValueError(
            "Insufficient OHLCV data: need at least 60 candles"
        )

    df: pd.DataFrame = pd.DataFrame(
        ohlcv,
        columns=["ts", "open", "high", "low", "close", "vol"]
    )

    df["ema20"] = EMAIndicator(df["close"], 20).ema_indicator()
    df["ema60"] = EMAIndicator(df["close"], 60).ema_indicator()

    latest: pd.Series = df.iloc[-1]

    near_support: bool = latest["close"] <= latest["ema60"] * 1.02
    positive_momentum: bool = latest["ema20"] >= latest["ema60"]

    return near_support and positive_momentum
