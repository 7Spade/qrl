import pandas as pd
from ta.trend import EMAIndicator

def should_buy(ohlcv: list) -> bool:
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
