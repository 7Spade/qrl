"""
Web dashboard for monitoring QRL trading bot.

This FastAPI application provides a comprehensive web interface to view:
- Current market data (price, 24h change, volume)
- Position status and risk metrics
- Strategy indicators (EMA20, EMA60)
- Trading signal analysis
- Configuration parameters

Usage:
    uvicorn app:app --reload
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import create_engine, text
import ccxt
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SYMBOL, BASE_ORDER_USDT, MAX_POSITION_USDT, PRICE_OFFSET, TIMEFRAME
from strategy import should_buy
from risk import can_buy

app = FastAPI(title="QRL Trading Bot Dashboard")
templates = Jinja2Templates(directory="web/templates")

engine = create_engine("sqlite:///data/state.db")
exchange = ccxt.mexc({"enableRateLimit": True})

def get_strategy_data():
    """
    Calculate strategy indicators and signals.
    
    Returns:
        dict: Strategy data including EMA values and buy signal
    """
    try:
        import pandas as pd
        from ta.trend import EMAIndicator
        
        ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=120)
        df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "vol"])
        
        df["ema20"] = EMAIndicator(df["close"], 20).ema_indicator()
        df["ema60"] = EMAIndicator(df["close"], 60).ema_indicator()
        
        latest = df.iloc[-1]
        
        buy_signal = should_buy(ohlcv)
        
        return {
            "ema20": round(float(latest["ema20"]), 6),
            "ema60": round(float(latest["ema60"]), 6),
            "close": round(float(latest["close"]), 6),
            "buy_signal": buy_signal,
            "ema_trend": "上升趨勢" if latest["ema20"] >= latest["ema60"] else "下降趨勢",
            "price_vs_ema60": round((float(latest["close"]) / float(latest["ema60"]) - 1) * 100, 2)
        }
    except Exception as e:
        return {
            "ema20": "N/A",
            "ema60": "N/A",
            "close": "N/A",
            "buy_signal": False,
            "ema_trend": "N/A",
            "price_vs_ema60": "N/A"
        }

@app.get("/health")
def health_check():
    """
    Health check endpoint for Cloud Run.
    
    Returns:
        JSONResponse: Health status
    """
    return JSONResponse({"status": "healthy", "service": "qrl-bot"})

@app.get("/api/data")
def get_data():
    """
    API endpoint for dashboard data.
    
    Returns:
        JSONResponse: All dashboard data in JSON format
    """
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        strategy_data = get_strategy_data()
        
        with engine.connect() as conn:
            try:
                pos = conn.execute(text("SELECT pos FROM state")).fetchone()
                position = pos[0] if pos else 0
            except:
                position = 0
        
        can_trade = can_buy(position, MAX_POSITION_USDT)
        
        return JSONResponse({
            "price": ticker.get("last", "N/A"),
            "change_24h": round(ticker.get("percentage", 0), 2),
            "volume_24h": round(ticker.get("quoteVolume", 0), 2),
            "high_24h": ticker.get("high", "N/A"),
            "low_24h": ticker.get("low", "N/A"),
            "position": round(position, 2),
            "position_pct": round((position / MAX_POSITION_USDT) * 100, 1),
            "can_buy": can_trade,
            "strategy": strategy_data,
            "config": {
                "base_order": BASE_ORDER_USDT,
                "max_position": MAX_POSITION_USDT,
                "price_offset": PRICE_OFFSET,
                "symbol": SYMBOL
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """
    Render the main dashboard page.
    
    Displays comprehensive trading bot status including:
    - Market data
    - Position and risk metrics
    - Strategy indicators
    - Trading signals
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTMLResponse: Rendered dashboard HTML
    """
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        strategy_data = get_strategy_data()
    except Exception as e:
        ticker = {"last": "N/A", "percentage": 0, "quoteVolume": 0, "high": "N/A", "low": "N/A"}
        strategy_data = {
            "ema20": "N/A",
            "ema60": "N/A",
            "close": "N/A",
            "buy_signal": False,
            "ema_trend": "N/A",
            "price_vs_ema60": "N/A"
        }

    with engine.connect() as conn:
        try:
            pos = conn.execute(text("SELECT pos FROM state")).fetchone()
            position = pos[0] if pos else 0
        except:
            position = 0

    can_trade = can_buy(position, MAX_POSITION_USDT)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "symbol": SYMBOL,
            "price": ticker.get("last", "N/A"),
            "change_24h": round(ticker.get("percentage", 0), 2),
            "volume_24h": round(ticker.get("quoteVolume", 0), 2),
            "high_24h": ticker.get("high", "N/A"),
            "low_24h": ticker.get("low", "N/A"),
            "position": round(position, 2),
            "position_pct": round((position / MAX_POSITION_USDT) * 100, 1),
            "max_position": MAX_POSITION_USDT,
            "base_order": BASE_ORDER_USDT,
            "price_offset": PRICE_OFFSET,
            "can_buy": can_trade,
            "ema20": strategy_data["ema20"],
            "ema60": strategy_data["ema60"],
            "ema_trend": strategy_data["ema_trend"],
            "price_vs_ema60": strategy_data["price_vs_ema60"],
            "buy_signal": strategy_data["buy_signal"],
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        },
    )
