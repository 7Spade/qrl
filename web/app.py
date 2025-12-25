from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import create_engine, text
import ccxt
import os
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")

engine = create_engine("sqlite:///data/state.db")

exchange = ccxt.mexc({"enableRateLimit": True})

SYMBOL = "QRL/USDT"

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    price = exchange.fetch_ticker(SYMBOL)["last"]

    with engine.connect() as conn:
        pos = conn.execute(text("SELECT pos FROM state")).fetchone()
        position = pos[0] if pos else 0

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
