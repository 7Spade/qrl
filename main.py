"""
Main execution script for QRL trading bot.

This script orchestrates the complete trading cycle:
1. Fetch historical market data
2. Evaluate trading strategy
3. Check risk management rules
4. Place limit buy orders
5. Update position state

Usage:
    python main.py
"""
from typing import List, Any
import sys
import ccxt
from exchange import get_exchange
from strategy import should_buy
from risk import can_buy
from state import get_position_usdt, update_position_usdt
from config import (
    SYMBOL,
    BASE_ORDER_USDT,
    MAX_POSITION_USDT,
    PRICE_OFFSET,
)


def fetch_market_data(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str = "1d",
    limit: int = 120
) -> List[List[Any]]:
    """
    Fetch OHLCV market data from exchange.

    Args:
        exchange: CCXT exchange instance
        symbol: Trading pair symbol (e.g., 'QRL/USDT')
        timeframe: Candlestick timeframe (default: '1d')
        limit: Number of candles to fetch (default: 120)

    Returns:
        List of OHLCV candles

    Raises:
        ccxt.NetworkError: When network connection fails
        ccxt.ExchangeError: When exchange API returns an error
    """
    try:
        ohlcv: List[List[Any]] = exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=limit
        )
        return ohlcv
    except ccxt.NetworkError as e:
        print(f"❌ 網路錯誤: {e}")
        raise
    except ccxt.ExchangeError as e:
        print(f"❌ 交易所錯誤: {e}")
        raise


def place_limit_buy_order(
    exchange: ccxt.Exchange,
    symbol: str,
    amount: float,
    price: float
) -> None:
    """
    Place a limit buy order on the exchange.

    Args:
        exchange: CCXT exchange instance
        symbol: Trading pair symbol
        amount: Amount of asset to buy
        price: Limit price for the order

    Raises:
        ccxt.InsufficientFunds: When account has insufficient balance
        ccxt.InvalidOrder: When order parameters are invalid
    """
    try:
        exchange.create_limit_buy_order(symbol, amount, price)
    except ccxt.InsufficientFunds as e:
        print(f"❌ 餘額不足: {e}")
        raise
    except ccxt.InvalidOrder as e:
        print(f"❌ 無效訂單: {e}")
        raise


def main() -> None:
    """
    Execute the main trading logic.

    This function orchestrates the complete trading cycle including
    market data fetching, strategy evaluation, risk checks, and
    order placement.
    """
    try:
        exchange: ccxt.Exchange = get_exchange()

        ohlcv: List[List[Any]] = fetch_market_data(
            exchange,
            SYMBOL,
            timeframe="1d",
            limit=120
        )

        if not should_buy(ohlcv):
            print("❌ 條件不成立，不買")
            sys.exit(0)

        position: float = get_position_usdt()

        if not can_buy(position, MAX_POSITION_USDT):
            print("⚠️ 已達最大倉位")
            sys.exit(0)

        ticker = exchange.fetch_ticker(SYMBOL)
        price: float = ticker["last"] * PRICE_OFFSET
        amount: float = BASE_ORDER_USDT / price

        place_limit_buy_order(exchange, SYMBOL, amount, price)
        update_position_usdt(position + BASE_ORDER_USDT)

        print(f"✅ 掛單完成 @ {price}")

    except Exception as e:
        print(f"❌ 執行錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
