"""
Configuration module for QRL trading bot.

This module loads environment variables and defines trading parameters
including position limits, order sizes, and price offsets.
"""
import os
from dotenv import load_dotenv


load_dotenv()

SYMBOL: str = os.getenv("SYMBOL", "QRL/USDT")
TIMEFRAME: str = "1d"
BASE_ORDER_USDT: float = 50.0
MAX_POSITION_USDT: float = 500.0
PRICE_OFFSET: float = 0.98
