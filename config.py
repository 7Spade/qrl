"""
Configuration module for QRL trading bot.

This module loads environment variables and defines trading parameters
including position limits, order sizes, and price offsets.
"""
from dotenv import load_dotenv
import os

load_dotenv()

SYMBOL = os.getenv("SYMBOL", "QRL/USDT")

TIMEFRAME = "1d"          # QRL 用日線最穩
BASE_ORDER_USDT = 50      # 單筆最多用多少 USDT
MAX_POSITION_USDT = 500   # QRL 最大曝險
PRICE_OFFSET = 0.98       # 限價折讓（不追價）
