"""
Trading strategy module implementing EMA-based buy signals.

This module analyzes historical price data using Exponential Moving Averages
to identify favorable entry points for accumulating QRL tokens.
"""
import pandas as pd
from ta.trend import EMAIndicator

def should_buy(ohlcv: list) -> bool:
    """
    Determine if conditions are favorable for buying based on EMA indicators.
    
    Buy signal conditions:
    1. Current price is within 2% of the 60-period EMA (near support)
    2. 20-period EMA is above or equal to 60-period EMA (positive momentum)
    
    Args:
        ohlcv: List of OHLCV candles [timestamp, open, high, low, close, volume]
        
    Returns:
        bool: True if buy conditions are met, False otherwise
    """
    df = pd.DataFrame(
        ohlcv, columns=["ts", "open", "high", "low", "close", "vol"]
    )

    df["ema20"] = EMAIndicator(df["close"], 20).ema_indicator()
    df["ema60"] = EMAIndicator(df["close"], 60).ema_indicator()

    latest = df.iloc[-1]

    # 低風險累積條件
    return (
        latest["close"] <= latest["ema60"] * 1.02
        and latest["ema20"] >= latest["ema60"]
    )
