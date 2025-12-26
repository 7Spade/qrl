"""
Web dashboard for monitoring QRL trading bot.

This FastAPI application provides a simple web interface to view:
- Current QRL/USDT price
- Total position value
- Last update timestamp

Usage:
    uvicorn app:app --reload
"""
from typing import Dict, Any
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import SQLAlchemyError
import ccxt


app = FastAPI(title="QRL Trading Bot Dashboard")
templates = Jinja2Templates(directory="web/templates")

engine: Engine = create_engine("sqlite:///data/state.db")
exchange: ccxt.Exchange = ccxt.mexc({"enableRateLimit": True})

SYMBOL: str = "QRL/USDT"


@app.get("/health")
def health_check() -> JSONResponse:
    """
    Health check endpoint for Cloud Run.

    Returns:
        JSONResponse: Health status
    """
    return JSONResponse({"status": "healthy", "service": "qrl-bot"})


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """
    Render the main dashboard page.

    Displays current market price, position value, and timestamp.

    Args:
        request: FastAPI request object

    Returns:
        HTMLResponse: Rendered dashboard HTML
    """
    price: Any = "N/A"
    try:
        ticker: Dict[str, Any] = exchange.fetch_ticker(SYMBOL)
        price = ticker["last"]
    except ccxt.NetworkError as e:
        print(f"❌ 網路錯誤: {e}")
    except ccxt.ExchangeError as e:
        print(f"❌ 交易所錯誤: {e}")
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")

    position: float = 0.0
    try:
        with engine.connect() as conn:
            pos = conn.execute(text("SELECT pos FROM state")).fetchone()
            position = float(pos[0]) if pos else 0.0
    except SQLAlchemyError as e:
        print(f"❌ 資料庫錯誤: {e}")
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "price": price,
            "position": position,
            "symbol": SYMBOL,
            "time": datetime.utcnow().isoformat(),
        },
    )
