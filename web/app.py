"""
Enhanced web dashboard for QRL trading bot.

Provides comprehensive monitoring including:
- Market data with EMA indicators
- Position status and utilization
- Trade history
- System logs
- Strategy status

Usage:
    uvicorn web.app_new:app --reload
"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
import ccxt
from src.core.config import AppConfig
from src.data.state import StateManager
from src.data.exchange import ExchangeClient
from src.strategies.ema_strategy import EMAAccumulationStrategy


app = FastAPI(title="QRL Trading Bot Dashboard")
templates = Jinja2Templates(directory="web/templates")

# Initialize components
config = AppConfig.load()
state_manager = StateManager()
exchange_client = ExchangeClient(config.exchange)
strategy = EMAAccumulationStrategy()


@app.get("/health")
def health_check() -> JSONResponse:
    """
    Health check endpoint for Cloud Run.
    
    Returns:
        JSONResponse: Health status
    """
    return JSONResponse({
        "status": "healthy",
        "service": "qrl-bot",
        "version": "2.0.0"
    })


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """
    Render enhanced dashboard page.
    
    Displays:
    - Current price and 24h change
    - EMA20 and EMA60 values
    - Position status and utilization
    - Strategy status
    - System health
    
    Args:
        request: FastAPI request object
    
    Returns:
        HTMLResponse: Rendered dashboard HTML
    """
    context = {
        "request": request,
        "symbol": config.trading.symbol,
        "price": "N/A",
        "price_raw": 0.0,
        "change_24h": "N/A",
        "change_24h_raw": 0.0,
        "ema20": "N/A",
        "ema20_raw": 0.0,
        "ema60": "N/A",
        "ema60_raw": 0.0,
        "position": 0.0,
        "max_position": config.trading.max_position_usdt,
        "utilization": 0.0,
        "available": config.trading.max_position_usdt,
        "strategy_status": "Unknown",
        "strategy_detail": "",
        "buy_condition": "",
        "api_status": "Disconnected",
        "data_delay": "N/A",
        "last_trade": "No trades yet",
        "last_update": datetime.utcnow().isoformat(),
        "config": config,  # Pass config to template
    }
    
    # Fetch market data
    start_time = datetime.utcnow()
    try:
        ticker = exchange_client.fetch_ticker(config.trading.symbol)
        context["price"] = f"${ticker['last']:.6f}"
        context["price_raw"] = ticker['last']
        context["change_24h"] = f"{ticker.get('percentage', 0):.2f}%"
        context["change_24h_raw"] = ticker.get('percentage', 0)
        context["api_status"] = "Connected"
        
        # Calculate data delay
        end_time = datetime.utcnow()
        delay_ms = (end_time - start_time).total_seconds() * 1000
        context["data_delay"] = f"{delay_ms:.0f}ms"
        
        # Fetch OHLCV for EMA calculation
        ohlcv = exchange_client.fetch_ohlcv(
            config.trading.symbol,
            config.trading.timeframe,
            limit=120
        )
        
        # Analyze with strategy
        signal = strategy.analyze(ohlcv)
        context["ema20"] = f"${signal.metadata.get('ema_short', 0):.6f}"
        context["ema20_raw"] = signal.metadata.get('ema_short', 0)
        context["ema60"] = f"${signal.metadata.get('ema_long', 0):.6f}"
        context["ema60_raw"] = signal.metadata.get('ema_long', 0)
        
        # Strategy status with details
        ema60_threshold = context["ema60_raw"] * 1.02
        context["buy_condition"] = f"Price ≤ ${ema60_threshold:.6f} (EMA60 × 1.02)"
        
        if signal.should_buy:
            context["strategy_status"] = "🟢 Buy Signal"
            context["strategy_detail"] = "Conditions met - Ready to buy"
        else:
            near_support = signal.metadata.get('near_support', False)
            positive_momentum = signal.metadata.get('positive_momentum', False)
            
            if not near_support and not positive_momentum:
                context["strategy_status"] = "⚠️ No Signal"
                context["strategy_detail"] = "Price too high & Momentum weak"
            elif not near_support:
                context["strategy_status"] = "⚠️ Waiting"
                context["strategy_detail"] = "Price above threshold"
            elif not positive_momentum:
                context["strategy_status"] = "⚠️ Waiting"
                context["strategy_detail"] = "Weak momentum (EMA20 < EMA60)"
            else:
                context["strategy_status"] = "⚠️ Hold"
                context["strategy_detail"] = "Monitoring conditions"
    
    except ccxt.NetworkError:
        context["api_status"] = "Network Error"
    except Exception as e:
        context["api_status"] = f"Error: {str(e)[:50]}"
    
    # Get position data
    try:
        position = state_manager.get_position()
        context["position"] = position
        context["utilization"] = (
            (position / config.trading.max_position_usdt) * 100
        )
        context["available"] = config.trading.max_position_usdt - position
        
        # Get last trade info
        trades = state_manager.get_trade_history(limit=1)
        if trades:
            last_trade = trades[0]
            trade_time = datetime.fromisoformat(last_trade['timestamp'])
            context["last_trade"] = f"{trade_time.strftime('%Y-%m-%d %H:%M UTC')}"
        
    except Exception:
        pass
    
    return templates.TemplateResponse("index.html", context)


@app.get("/api/trades")
def get_trades(limit: int = 20) -> JSONResponse:
    """
    Get recent trade history.
    
    Args:
        limit: Maximum number of trades to return
    
    Returns:
        JSONResponse: List of recent trades
    """
    try:
        trades = state_manager.get_trade_history(limit)
        return JSONResponse({"trades": trades})
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/statistics")
def get_statistics() -> JSONResponse:
    """
    Get trading statistics.
    
    Returns:
        JSONResponse: Trading statistics
    """
    try:
        stats = state_manager.get_statistics()
        return JSONResponse(stats)
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/logs")
def get_logs(limit: int = 50) -> JSONResponse:
    """
    Get recent system logs.
    
    Args:
        limit: Maximum number of log lines to return
    
    Returns:
        JSONResponse: Recent log entries
    """
    try:
        log_file = Path(config.monitoring.log_file)
        if not log_file.exists():
            return JSONResponse({"logs": []})
        
        with open(log_file, "r") as f:
            lines = f.readlines()
            recent_logs = lines[-limit:] if len(lines) > limit else lines
        
        return JSONResponse({
            "logs": [line.strip() for line in recent_logs]
        })
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/market")
def get_market_data() -> JSONResponse:
    """
    Get current market data with indicators.
    
    Returns:
        JSONResponse: Market data and indicators
    """
    try:
        ticker = exchange_client.fetch_ticker(config.trading.symbol)
        ohlcv = exchange_client.fetch_ohlcv(
            config.trading.symbol,
            config.trading.timeframe,
            limit=120
        )
        
        signal = strategy.analyze(ohlcv)
        
        return JSONResponse({
            "symbol": config.trading.symbol,
            "price": ticker["last"],
            "change_24h": ticker.get("percentage", 0),
            "volume_24h": ticker.get("quoteVolume", 0),
            "ema20": signal.metadata.get("ema_short", 0),
            "ema60": signal.metadata.get("ema_long", 0),
            "buy_signal": signal.should_buy,
            "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
