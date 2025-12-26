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
import logging
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


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="QRL Trading Bot Dashboard")
templates = Jinja2Templates(directory="web/templates")

# Initialize components with error handling
try:
    config = AppConfig.load()
    state_manager = StateManager()
    exchange_client = ExchangeClient(config.exchange, cache_config=config.cache)
    strategy = EMAAccumulationStrategy()
    logger.info("✅ All components initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize components: {e}")
    # Create dummy objects to prevent crashes
    config = None
    state_manager = None
    exchange_client = None
    strategy = None


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


@app.get("/history", response_class=HTMLResponse)
def trade_history_page(request: Request) -> HTMLResponse:
    """
    Render trade history visualization page.
    
    Shows:
    - Summary statistics
    - Complete trade history table
    - Trade distribution analytics
    
    Args:
        request: FastAPI request object
    
    Returns:
        HTMLResponse: Rendered history page HTML
    """
    return templates.TemplateResponse("history.html", {"request": request})


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
    Get comprehensive trading statistics.
    
    Returns detailed metrics including:
    - Total trades and cost
    - Average price and amount
    - Position utilization
    - Win rate (if applicable)
    - Recent performance
    
    Returns:
        JSONResponse: Trading statistics
    """
    try:
        # Get basic statistics
        stats = state_manager.get_statistics()
        
        # Add position information
        current_position = state_manager.get_position()
        stats["current_position"] = current_position
        stats["max_position_usdt"] = config.trading.max_position_usdt
        stats["position_utilization_pct"] = (
            (current_position / config.trading.max_position_usdt) * 100
            if config.trading.max_position_usdt > 0 else 0
        )
        stats["available_capacity"] = config.trading.max_position_usdt - current_position
        
        # Add trading configuration
        stats["config"] = {
            "symbol": config.trading.symbol,
            "base_order_usdt": config.trading.base_order_usdt,
            "max_position_usdt": config.trading.max_position_usdt,
            "price_offset": config.trading.price_offset,
        }
        
        # Get recent trades for performance metrics
        recent_trades = state_manager.get_trade_history(limit=10)
        stats["recent_trades_count"] = len(recent_trades)
        
        if recent_trades:
            # Calculate total invested from recent trades
            recent_total = sum(t['cost'] for t in recent_trades)
            stats["recent_total_cost"] = recent_total
            
            # Get earliest and latest trade timestamps
            timestamps = [t['timestamp'] for t in recent_trades]
            stats["earliest_trade"] = min(timestamps)
            stats["latest_trade"] = max(timestamps)
        
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
    Get current market data with indicators and account balances.
    
    Returns:
        JSONResponse: Market data, indicators, and balances (QRL, USDT)
    """
    try:
        if not all([config, exchange_client, strategy]):
            return JSONResponse(
                {"error": "System not initialized properly. Check configuration."},
                status_code=500
            )
        
        ticker = exchange_client.fetch_ticker(config.trading.symbol)
        ohlcv = exchange_client.fetch_ohlcv(
            config.trading.symbol,
            config.trading.timeframe,
            limit=120
        )
        
        if not ohlcv or len(ohlcv) == 0:
            return JSONResponse(
                {"error": "OHLCV data is empty"},
                status_code=500
            )
        
        signal = strategy.analyze(ohlcv)
        
        # Fetch account balances
        balances = {"qrl": 0.0, "usdt": 0.0}
        try:
            balance_data = exchange_client.fetch_balance()
            if balance_data and "total" in balance_data:
                balances["qrl"] = float(balance_data["total"].get("QRL", 0))
                balances["usdt"] = float(balance_data["total"].get("USDT", 0))
        except Exception as e:
            logger.warning(f"Error fetching balances: {e}")
        
        return JSONResponse({
            "symbol": config.trading.symbol,
            "price": ticker["last"],
            "change_24h": ticker.get("percentage", 0),
            "volume_24h": ticker.get("quoteVolume", 0),
            "ema20": signal.metadata.get("ema_short", 0),
            "ema60": signal.metadata.get("ema_long", 0),
            "buy_signal": signal.should_buy,
            "timestamp": datetime.utcnow().isoformat(),
            "balances": balances
        })
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/market/chart-data")
def get_chart_data(timeframe: str = "1h") -> JSONResponse:
    """
    Get historical price and indicator data for chart visualization.
    Data is automatically cached in Redis per MEXC API integration.
    
    Args:
        timeframe: Timeframe for chart data (1m, 5m, 15m, 30m, 1h, 4h, 1d)
    
    Returns:
        JSONResponse: Chart data with timestamps, prices, volumes, MA, and EMA values
    """
    try:
        # Validate timeframe
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        if timeframe not in valid_timeframes:
            timeframe = "1h"
        
        # Fetch OHLCV data (automatically cached in Redis with 60s TTL)
        ohlcv = exchange_client.fetch_ohlcv(
            config.trading.symbol,
            timeframe,
            limit=100  # Last 100 candles for chart
        )
        
        if not ohlcv or len(ohlcv) == 0:
            return JSONResponse({"error": "No data available"}, status_code=404)
        
        # Calculate indicators for chart
        import pandas as pd
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calculate MAs and EMAs
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema60'] = df['close'].ewm(span=60, adjust=False).mean()
        
        # Prepare chart data
        chart_data = {
            "labels": [
                datetime.fromtimestamp(ts/1000).strftime('%m-%d %H:%M')
                for ts in df['timestamp'].tolist()
            ],
            "prices": df['close'].tolist(),
            "ma20": df['ma20'].fillna(0).tolist(),
            "ma60": df['ma60'].fillna(0).tolist(),
            "ema20": df['ema20'].tolist(),
            "ema60": df['ema60'].tolist(),
            "volumes": df['volume'].tolist(),
            "metadata": {
                "symbol": config.trading.symbol,
                "timeframe": timeframe,
                "data_points": len(df),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        return JSONResponse(chart_data)
    except Exception as e:
        logger.error(f"Error fetching chart data: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/market/indicators")
def get_indicators(timeframe: str = "1h") -> JSONResponse:
    """
    Get technical indicators calculated from Redis-cached MEXC OHLCV data.
    Includes Williams %R, MACD, RSI, MA, and Volume analysis.
    
    Args:
        timeframe: Timeframe for indicators (1m, 5m, 15m, 30m, 1h, 4h, 1d)
    
    Returns:
        JSONResponse: Technical indicators data
    """
    try:
        import pandas as pd
        
        # Validate timeframe
        valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        if timeframe not in valid_timeframes:
            timeframe = "1h"
        
        # Fetch OHLCV data (automatically cached in Redis)
        ohlcv = exchange_client.fetch_ohlcv(
            config.trading.symbol,
            timeframe,
            limit=100
        )
        
        if not ohlcv or len(ohlcv) == 0:
            return JSONResponse({"error": "No data available"}, status_code=404)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Williams %R (14-period)
        period = 14
        df['highest_high'] = df['high'].rolling(window=period).max()
        df['lowest_low'] = df['low'].rolling(window=period).min()
        df['williams_r'] = ((df['highest_high'] - df['close']) / 
                           (df['highest_high'] - df['lowest_low'])) * -100
        
        # MACD (12, 26, 9)
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI (14-period)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MA (20, 60)
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        # Volume color (green if close > open, red otherwise)
        df['volume_color'] = df.apply(lambda row: 'rgba(0, 255, 0, 0.7)' if row['close'] >= row['open'] else 'rgba(255, 0, 0, 0.7)', axis=1)
        
        indicators_data = {
            "timeframe": timeframe,
            "labels": [
                datetime.fromtimestamp(ts/1000).strftime('%m-%d %H:%M')
                for ts in df['timestamp'].tolist()
            ],
            "williams_r": df['williams_r'].fillna(0).tolist(),
            "macd": df['macd'].fillna(0).tolist(),
            "macd_signal": df['macd_signal'].fillna(0).tolist(),
            "macd_histogram": df['macd_histogram'].fillna(0).tolist(),
            "rsi": df['rsi'].fillna(50).tolist(),
            "ma20": df['ma20'].fillna(0).tolist(),
            "ma60": df['ma60'].fillna(0).tolist(),
            "volumes": df['volume'].tolist(),
            "volume_colors": df['volume_color'].tolist(),
            "metadata": {
                "symbol": config.trading.symbol,
                "timeframe": timeframe,
                "data_points": len(df),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        return JSONResponse(indicators_data)
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/performance")
def get_performance_metrics() -> JSONResponse:
    """
    Get detailed performance metrics and analytics.
    
    Calculates and returns:
    - Total investment and average cost
    - Trade frequency and distribution
    - Position metrics
    - System health indicators
    
    Returns:
        JSONResponse: Performance metrics
    """
    try:
        # Get all trade history
        all_trades = state_manager.get_trade_history(limit=1000)
        stats = state_manager.get_statistics()
        current_position = state_manager.get_position()
        
        # Calculate performance metrics
        metrics = {
            "overview": {
                "total_trades": len(all_trades),
                "total_invested": stats.get("total_cost", 0),
                "avg_purchase_price": stats.get("avg_price", 0),
                "current_position": current_position,
                "position_utilization_pct": (
                    (current_position / config.trading.max_position_usdt) * 100
                    if config.trading.max_position_usdt > 0 else 0
                ),
            },
            "trade_distribution": {},
            "time_analysis": {},
            "system_health": {
                "cache_enabled": config.cache.redis_enabled,
                "api_status": "healthy",  # Would be checked via actual health check
            }
        }
        
        if all_trades:
            # Analyze trade distribution by time
            from collections import Counter
            trade_hours = [
                datetime.fromisoformat(t['timestamp']).hour
                for t in all_trades
            ]
            hour_distribution = Counter(trade_hours)
            
            metrics["trade_distribution"] = {
                "by_hour": dict(hour_distribution.most_common(24)),
                "peak_hour": hour_distribution.most_common(1)[0][0] if hour_distribution else 0,
            }
            
            # Time analysis
            timestamps = [datetime.fromisoformat(t['timestamp']) for t in all_trades]
            if len(timestamps) > 1:
                time_diffs = [
                    (timestamps[i] - timestamps[i-1]).total_seconds() / 3600
                    for i in range(1, len(timestamps))
                ]
                metrics["time_analysis"] = {
                    "avg_hours_between_trades": sum(time_diffs) / len(time_diffs) if time_diffs else 0,
                    "min_hours_between_trades": min(time_diffs) if time_diffs else 0,
                    "max_hours_between_trades": max(time_diffs) if time_diffs else 0,
                }
        
        return JSONResponse(metrics)
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/market/deals")
def get_latest_deals() -> JSONResponse:
    """Get latest deals/trades data from MEXC (cached in Redis)."""
    try:
        deals = exchange_client.fetch_deals(
            config.trading.symbol,
            limit=20
        )
        return JSONResponse({
            "symbol": config.trading.symbol,
            "count": len(deals),
            "deals": deals[:10],  # Return first 10 for API response
            "cached": True  # Always try cache first
        })
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/market/depth")
def get_market_depth() -> JSONResponse:
    """Get market depth/order book data from MEXC (cached in Redis)."""
    try:
        depth = exchange_client.fetch_order_book(
            config.trading.symbol,
            limit=10
        )
        return JSONResponse({
            "symbol": config.trading.symbol,
            "bids": depth.get("bids", [])[:10],
            "asks": depth.get("asks", [])[:10],
            "timestamp": depth.get("timestamp"),
            "cached": True  # Always try cache first
        })
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/cache/stats")
def get_cache_stats() -> JSONResponse:
    """Get Redis cache statistics."""
    try:
        stats = exchange_client.get_cache_stats()
        return JSONResponse(stats)
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
