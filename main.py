import os
from exchange import get_exchange
from strategy import should_buy
from risk import can_buy
from state import get_position_usdt, update_position_usdt
from config import SYMBOL, BASE_ORDER_USDT, MAX_POSITION_USDT, PRICE_OFFSET

exchange = get_exchange()

ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe="1d", limit=120)

if not should_buy(ohlcv):
    print("❌ 條件不成立，不買")
    exit()

position = get_position_usdt()

if not can_buy(position, MAX_POSITION_USDT):
    print("⚠️ 已達最大倉位")
    exit()

ticker = exchange.fetch_ticker(SYMBOL)
price = ticker["last"] * PRICE_OFFSET
amount = BASE_ORDER_USDT / price

exchange.create_limit_buy_order(
    SYMBOL,
    amount,
    price
)

update_position_usdt(position + BASE_ORDER_USDT)

print(f"✅ 掛單完成 @ {price}")
