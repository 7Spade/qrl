"""Data update callbacks for the dashboard."""
from dash import html, Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
import logging

from web.components.cards import (
    create_status_banner,
    create_market_data_card,
    create_position_card,
    create_strategy_card,
    create_system_card,
    create_trade_history_table
)
from web.components.charts import (
    create_price_chart,
    create_indicators_chart,
    calculate_indicators
)

logger = logging.getLogger(__name__)


def register_callbacks(app, config, state_manager, exchange_client, 
                       initialization_error):
    """
    Register all data update callbacks.
    
    Args:
        app: Dash app instance
        config: Application configuration
        state_manager: State manager instance
        exchange_client: Exchange client instance
        initialization_error: Initialization error message if any
    """
    
    @app.callback(
        Output('status-banner', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_status_banner(n):
        """Update status banner."""
        return create_status_banner(initialization_error)
    
    @app.callback(
        Output('market-data', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_market_data(n):
        """Update market data display."""
        if not exchange_client or not config:
            return html.P("Service not initialized", className="text-danger")
        
        try:
            ticker = exchange_client.fetch_ticker(config.trading.symbol)
            ohlcv = exchange_client.fetch_ohlcv(
                config.trading.symbol, 
                config.trading.timeframe,  # Use config timeframe instead of hardcoded '1h'
                limit=120
            )
            
            if not ohlcv or len(ohlcv) == 0:
                logger.warning(f"OHLCV data empty for {config.trading.symbol} timeframe={config.trading.timeframe}")
                return html.P(
                    "⚠️ Waiting for market data...",
                    className="text-warning"
                )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            ema20 = df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ema60 = df['close'].ewm(span=60, adjust=False).mean().iloc[-1]
            
            logger.info(f"Market data loaded: {len(ohlcv)} candles, price={ticker.get('last', 0)}")
            
            return create_market_data_card(
                symbol=config.trading.symbol,
                price=ticker.get('last', 0),
                change_24h=ticker.get('percentage', 0),
                ema20=ema20,
                ema60=ema60
            )
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    @app.callback(
        Output('position-data', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_position_data(n):
        """Update position data display."""
        if not state_manager or not config or not exchange_client:
            return html.P("Service not initialized", className="text-danger")
        
        try:
            stats = state_manager.get_statistics()
            current_position = state_manager.get_position()
            
            # Get balances from exchange
            qrl_balance = 0.0
            usdt_balance = 0.0
            try:
                balance_data = exchange_client.fetch_balance()
                if balance_data and "total" in balance_data:
                    qrl_balance = float(balance_data["total"].get("QRL", 0))
                    usdt_balance = float(balance_data["total"].get("USDT", 0))
                    logger.info(f"Fetched balances: QRL={qrl_balance}, USDT={usdt_balance}")
                else:
                    logger.warning(f"Balance data structure unexpected: {balance_data.keys() if balance_data else 'None'}")
            except Exception as e:
                logger.warning(f"Error fetching balances: {e}")
            
            utilization = (
                (current_position / config.trading.max_position_usdt * 100)
                if config.trading.max_position_usdt > 0 else 0
            )
            
            return create_position_card(
                qrl_balance=qrl_balance,
                usdt_balance=usdt_balance,
                current_position=current_position,
                max_position=config.trading.max_position_usdt,
                utilization=utilization
            )
        except Exception as e:
            logger.error(f"Error fetching position data: {e}")
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    @app.callback(
        Output('strategy-data', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_strategy_data(n):
        """Update strategy status display."""
        if not exchange_client or not config or not state_manager:
            return html.P("Service not initialized", className="text-danger")
        
        try:
            ticker = exchange_client.fetch_ticker(config.trading.symbol)
            ohlcv = exchange_client.fetch_ohlcv(
                config.trading.symbol, 
                config.trading.timeframe,  # Use config timeframe instead of hardcoded '1h'
                limit=120
            )
            
            if not ohlcv or len(ohlcv) == 0:
                logger.warning(f"OHLCV data empty for strategy, symbol={config.trading.symbol} timeframe={config.trading.timeframe}")
                return html.P(
                    "⚠️ Waiting for market data...",
                    className="text-warning"
                )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            ema20 = df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ema60 = df['close'].ewm(span=60, adjust=False).mean().iloc[-1]
            
            price = ticker.get('last', 0)
            buy_threshold = ema60 * 1.02
            buy_signal = price <= buy_threshold and ema20 >= ema60
            
            stats = state_manager.get_statistics()
            last_trade = stats.get('last_trade_time', 'None')
            
            logger.info(f"Strategy data loaded: signal={buy_signal}, price={price}, ema20={ema20}, ema60={ema60}")
            
            return create_strategy_card(
                buy_signal=buy_signal,
                buy_threshold=buy_threshold,
                price=price,
                ema20=ema20,
                ema60=ema60,
                last_trade=last_trade
            )
        except Exception as e:
            logger.error(f"Error fetching strategy data: {e}")
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    @app.callback(
        Output('system-data', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_system_data(n):
        """Update system status display."""
        try:
            health_status = 'healthy' if not initialization_error else 'error'
            
            cache_enabled = False
            cache_connected = False
            cache_keys = 0
            
            if exchange_client and config:
                try:
                    cache_stats = exchange_client.get_cache_stats()
                    cache_enabled = cache_stats.get('enabled', False)
                    cache_connected = cache_stats.get('status') == 'connected'
                    cache_keys = cache_stats.get('cache_keys', 0)
                except Exception as e:
                    logger.warning(f"Error fetching cache stats: {e}")
            
            return create_system_card(
                health_status=health_status,
                cache_enabled=cache_enabled,
                cache_connected=cache_connected,
                cache_keys=cache_keys
            )
        except Exception as e:
            logger.error(f"Error fetching system data: {e}")
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    @app.callback(
        Output('trade-history', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_trade_history(n):
        """Update trade history display."""
        if not state_manager:
            return html.P("Service not initialized", className="text-danger")
        
        try:
            trades = state_manager.get_trade_history(limit=10)
            
            if not trades:
                return html.P("No trades yet", className="text-muted")
            
            return create_trade_history_table(trades)
        except Exception as e:
            logger.error(f"Error fetching trade history: {e}")
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    @app.callback(
        Output('last-update', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_timestamp(n):
        """Update the last update timestamp."""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
