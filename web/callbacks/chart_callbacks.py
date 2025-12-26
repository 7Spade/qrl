"""Chart update callbacks for the dashboard."""
from dash import Input, Output
import plotly.graph_objs as go
import pandas as pd
import logging

from web.components.charts import (
    create_price_chart,
    create_indicators_chart,
    calculate_indicators
)

logger = logging.getLogger(__name__)


def register_callbacks(app, config, exchange_client):
    """
    Register chart update callbacks.
    
    Args:
        app: Dash app instance
        config: Application configuration
        exchange_client: Exchange client instance
    """
    
    @app.callback(
        Output('price-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('timeframe-selector', 'value')]
    )
    def update_price_chart(n, timeframe):
        """Update price chart with candlesticks and moving averages."""
        if not exchange_client or not config:
            return go.Figure()
        
        try:
            ohlcv = exchange_client.fetch_ohlcv(
                config.trading.symbol,
                timeframe,
                limit=100
            )
            
            if not ohlcv or len(ohlcv) == 0:
                return go.Figure().add_annotation(
                    text="Waiting for market data...",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = calculate_indicators(df)
            
            return create_price_chart(df, config.trading.symbol)
        except Exception as e:
            logger.error(f"Error creating price chart: {e}")
            return go.Figure().add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    @app.callback(
        Output('indicators-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('timeframe-selector', 'value')]
    )
    def update_indicators_chart(n, timeframe):
        """Update technical indicators chart."""
        if not exchange_client or not config:
            return go.Figure()
        
        try:
            ohlcv = exchange_client.fetch_ohlcv(
                config.trading.symbol,
                timeframe,
                limit=100
            )
            
            if not ohlcv or len(ohlcv) == 0:
                return go.Figure()
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = calculate_indicators(df)
            
            return create_indicators_chart(df)
        except Exception as e:
            logger.error(f"Error creating indicators chart: {e}")
            return go.Figure()
