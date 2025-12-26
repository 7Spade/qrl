"""
Web dashboard for monitoring QRL trading bot.

This FastAPI application provides a simple web interface to view:
- Current QRL/USDT price
- Total position value
- Last update timestamp

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
from datetime import datetime

app = FastAPI(title="QRL Trading Bot Dashboard")
templates = Jinja2Templates(directory="web/templates")

engine = create_engine("sqlite:///data/state.db")

exchange = ccxt.mexc({"enableRateLimit": True})

SYMBOL = "QRL/USDT"

@app.get("/health")
def health_check():
    """
    Health check endpoint for Cloud Run.
    
    Returns:
        JSONResponse: Health status
    """
    return JSONResponse({"status": "healthy", "service": "qrl-bot"})

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """
    Render the main dashboard page.
    
    Displays current market price, position value, and timestamp.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTMLResponse: Rendered dashboard HTML
    """
    try:
        price = exchange.fetch_ticker(SYMBOL)["last"]
    except Exception as e:
        price = "N/A"

    with engine.connect() as conn:
        try:
            pos = conn.execute(text("SELECT pos FROM state")).fetchone()
            position = pos[0] if pos else 0
        except:
            position = 0

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
