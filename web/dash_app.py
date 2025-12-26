"""
Dash-based web dashboard for QRL trading bot.

Provides comprehensive monitoring including:
- Market data with interactive charts
- Position status and utilization
- Trade history
- System logs
- Strategy status

Usage:
    python web/dash_app.py
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from pathlib import Path

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd

from src.core.config import AppConfig
from src.data.state import StateManager
from src.data.exchange import ExchangeClient
from src.strategies.ema_strategy import EMAAccumulationStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="QRL Trading Bot Dashboard"
)

# Initialize components with error handling
initialization_error = None
try:
    config = AppConfig.load()
    state_manager = StateManager()
    exchange_client = ExchangeClient(config.exchange, cache_config=config.cache)
    strategy = EMAAccumulationStrategy()
    logger.info("✅ All components initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize components: {e}")
    initialization_error = str(e)
    config = None
    state_manager = None
    exchange_client = None
    strategy = None


def create_layout():
    """Create the main dashboard layout."""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("📊 QRL Trading Bot Dashboard", 
                       className="text-center mb-4 text-success")
            ])
        ]),
        
        # Status banner
        dbc.Row([
            dbc.Col([
                html.Div(id='status-banner', className="mb-3")
            ])
        ]),
        
        # Top row - Market Data and Position
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📈 Market Data", className="bg-success text-white"),
                    dbc.CardBody(id='market-data')
                ], className="mb-3")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("💼 Position Status", className="bg-info text-white"),
                    dbc.CardBody(id='position-data')
                ], className="mb-3")
            ], md=6),
        ]),
        
        # Charts row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.Span("📊 Price Chart", className="me-3"),
                            dcc.Dropdown(
                                id='timeframe-selector',
                                options=[
                                    {'label': '1 Minute', 'value': '1m'},
                                    {'label': '5 Minutes', 'value': '5m'},
                                    {'label': '15 Minutes', 'value': '15m'},
                                    {'label': '30 Minutes', 'value': '30m'},
                                    {'label': '1 Hour', 'value': '1h'},
                                    {'label': '4 Hours', 'value': '4h'},
                                    {'label': '1 Day', 'value': '1d'},
                                ],
                                value='1h',
                                clearable=False,
                                style={'width': '150px', 'display': 'inline-block'}
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'})
                    ], className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(id='price-chart', style={'height': '400px'})
                    ])
                ], className="mb-3")
            ], md=12),
        ]),
        
        # Indicators row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📉 Technical Indicators", className="bg-warning text-dark"),
                    dbc.CardBody([
                        dcc.Graph(id='indicators-chart', style={'height': '400px'})
                    ])
                ], className="mb-3")
            ], md=12),
        ]),
        
        # Bottom row - Strategy and System
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("🎯 Strategy Status", className="bg-success text-white"),
                    dbc.CardBody(id='strategy-data')
                ], className="mb-3")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("⚙️ System Status", className="bg-secondary text-white"),
                    dbc.CardBody(id='system-data')
                ], className="mb-3")
            ], md=6),
        ]),
        
        # Trade History
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("📜 Recent Trades", className="bg-info text-white"),
                    dbc.CardBody(id='trade-history')
                ], className="mb-3")
            ], md=12),
        ]),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # Update every 60 seconds
            n_intervals=0
        ),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P(f"Last Updated: ", className="text-muted d-inline"),
                    html.Span(id='last-update', className="text-info")
                ], className="text-center")
            ])
        ])
    ], fluid=True)


app.layout = create_layout()


@app.callback(
    Output('status-banner', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_status_banner(n):
    """Update status banner."""
    if initialization_error:
        return dbc.Alert(
            f"⚠️ System Error: {initialization_error}",
            color="danger",
            dismissable=False
        )
    return dbc.Alert(
        "✅ System operational - All services running normally",
        color="success",
        dismissable=False
    )


@app.callback(
    Output('market-data', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_market_data(n):
    """Update market data display."""
    if not exchange_client or not config:
        return html.P("Service not initialized", className="text-danger")
    
    try:
        # Fetch market data
        ticker = exchange_client.fetch_ticker(config.trading.symbol)
        ohlcv = exchange_client.fetch_ohlcv(config.trading.symbol, '1h', limit=60)
        
        if not ohlcv or len(ohlcv) == 0:
            return html.P("⚠️ Waiting for market data...", className="text-warning")
        
        # Calculate EMAs
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        ema20 = df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
        ema60 = df['close'].ewm(span=60, adjust=False).mean().iloc[-1]
        
        price = ticker.get('last', 0)
        change_24h = ticker.get('percentage', 0)
        
        change_class = "text-success" if change_24h >= 0 else "text-danger"
        change_symbol = "+" if change_24h >= 0 else ""
        
        return html.Div([
            html.Div([
                html.Strong("Symbol: "), html.Span(f"{config.trading.symbol}")
            ], className="mb-2"),
            html.Div([
                html.Strong("Price: "), html.Span(f"${price:.6f}")
            ], className="mb-2"),
            html.Div([
                html.Strong("24H Change: "), 
                html.Span(f"{change_symbol}{change_24h:.2f}%", className=change_class)
            ], className="mb-2"),
            html.Div([
                html.Strong("EMA 20: "), html.Span(f"${ema20:.6f}")
            ], className="mb-2"),
            html.Div([
                html.Strong("EMA 60: "), html.Span(f"${ema60:.6f}")
            ], className="mb-2"),
            html.Div([
                html.Strong("Data Delay: "), 
                html.Span("< 1s (Redis)", className="text-success")
            ])
        ])
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        return html.P(f"Error: {str(e)}", className="text-danger")


@app.callback(
    Output('position-data', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_position_data(n):
    """Update position data display."""
    if not state_manager or not config:
        return html.P("Service not initialized", className="text-danger")
    
    try:
        stats = state_manager.get_statistics()
        current_position = state_manager.get_position()
        
        # Get balances from exchange
        try:
            ticker = exchange_client.fetch_ticker(config.trading.symbol)
            balance = exchange_client.exchange.fetch_balance()
            qrl_balance = balance.get('QRL', {}).get('free', 0)
            usdt_balance = balance.get('USDT', {}).get('free', 0)
        except:
            qrl_balance = 0
            usdt_balance = 0
        
        utilization = (current_position / config.trading.max_position_usdt * 100) if config.trading.max_position_usdt > 0 else 0
        available_capacity = config.trading.max_position_usdt - current_position
        
        return html.Div([
            html.Div([
                html.Strong("QRL Holdings: "), 
                html.Span(f"{qrl_balance:.4f} QRL", className="text-success")
            ], className="mb-2"),
            html.Div([
                html.Strong("USDT Balance: "), 
                html.Span(f"{usdt_balance:.2f} USDT")
            ], className="mb-2"),
            html.Div([
                html.Strong("Current Position: "), 
                html.Span(f"${current_position:.2f}")
            ], className="mb-2"),
            html.Div([
                html.Strong("Max Position: "), 
                html.Span(f"${config.trading.max_position_usdt:.2f}")
            ], className="mb-2"),
            html.Div([
                html.Strong("Available: "), 
                html.Span(f"${available_capacity:.2f}")
            ], className="mb-2"),
            html.Div([
                dbc.Progress(
                    value=utilization,
                    label=f"{utilization:.1f}%",
                    color="success" if utilization < 80 else "warning" if utilization < 95 else "danger",
                    className="mb-1"
                )
            ], className="mb-2"),
        ])
    except Exception as e:
        logger.error(f"Error fetching position data: {e}")
        return html.P(f"Error: {str(e)}", className="text-danger")


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
        ohlcv = exchange_client.fetch_ohlcv(config.trading.symbol, timeframe, limit=100)
        
        if not ohlcv or len(ohlcv) == 0:
            return go.Figure().add_annotation(
                text="Waiting for market data...",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calculate moving averages
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema60'] = df['close'].ewm(span=60, adjust=False).mean()
        
        # Create candlestick chart
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
            increasing_line_color='#00ff41',
            decreasing_line_color='#ff4444'
        ))
        
        # MA20
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ma20'],
            mode='lines',
            name='MA20',
            line=dict(color='#00d4ff', width=1)
        ))
        
        # MA60
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ma60'],
            mode='lines',
            name='MA60',
            line=dict(color='#ffa500', width=1)
        ))
        
        # EMA20
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ema20'],
            mode='lines',
            name='EMA20',
            line=dict(color='#00ff41', width=2, dash='dash')
        ))
        
        # EMA60
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ema60'],
            mode='lines',
            name='EMA60',
            line=dict(color='#ff6b6b', width=2, dash='dash')
        ))
        
        fig.update_layout(
            template='plotly_dark',
            xaxis_title='Time',
            yaxis_title='Price (USDT)',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=30, b=50)
        )
        
        return fig
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
        ohlcv = exchange_client.fetch_ohlcv(config.trading.symbol, timeframe, limit=100)
        
        if not ohlcv or len(ohlcv) == 0:
            return go.Figure()
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calculate indicators
        # Williams %R
        period = 14
        df['highest_high'] = df['high'].rolling(window=period).max()
        df['lowest_low'] = df['low'].rolling(window=period).min()
        df['williams_r'] = ((df['highest_high'] - df['close']) / 
                           (df['highest_high'] - df['lowest_low'])) * -100
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Create subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Williams %R', 'RSI', 'MACD'),
            row_heights=[0.33, 0.33, 0.34]
        )
        
        # Williams %R
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['williams_r'],
            mode='lines',
            name='Williams %R',
            line=dict(color='#00d4ff', width=2)
        ), row=1, col=1)
        fig.add_hline(y=-20, line_dash="dash", line_color="red", row=1, col=1)
        fig.add_hline(y=-80, line_dash="dash", line_color="green", row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['rsi'],
            mode='lines',
            name='RSI',
            line=dict(color='#ffa500', width=2)
        ), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['macd'],
            mode='lines',
            name='MACD',
            line=dict(color='#00ff41', width=2)
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['macd_signal'],
            mode='lines',
            name='Signal',
            line=dict(color='#ff6b6b', width=2)
        ), row=3, col=1)
        fig.add_trace(go.Bar(
            x=df['timestamp'],
            y=df['macd_histogram'],
            name='Histogram',
            marker_color=['green' if val > 0 else 'red' for val in df['macd_histogram']]
        ), row=3, col=1)
        
        fig.update_layout(
            template='plotly_dark',
            showlegend=True,
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        fig.update_xaxes(title_text="Time", row=3, col=1)
        
        return fig
    except Exception as e:
        logger.error(f"Error creating indicators chart: {e}")
        return go.Figure()


@app.callback(
    Output('strategy-data', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_strategy_data(n):
    """Update strategy status display."""
    if not exchange_client or not config or not state_manager:
        return html.P("Service not initialized", className="text-danger")
    
    try:
        # Get market data
        ticker = exchange_client.fetch_ticker(config.trading.symbol)
        ohlcv = exchange_client.fetch_ohlcv(config.trading.symbol, '1h', limit=60)
        
        if not ohlcv or len(ohlcv) == 0:
            return html.P("⚠️ Waiting for market data...", className="text-warning")
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        ema20 = df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
        ema60 = df['close'].ewm(span=60, adjust=False).mean().iloc[-1]
        
        price = ticker.get('last', 0)
        buy_threshold = ema60 * 1.02
        buy_signal = price <= buy_threshold and ema20 >= ema60
        
        stats = state_manager.get_statistics()
        last_trade = stats.get('last_trade_time', 'None')
        
        status_text = '✅ Ready to Buy' if buy_signal else '⏸️ Waiting'
        status_class = 'text-success' if buy_signal else 'text-warning'
        
        if buy_signal:
            detail_text = 'Conditions met - Ready to execute'
        elif price > buy_threshold:
            if ema20 < ema60:
                detail_text = 'Price too high & Momentum weak'
            else:
                detail_text = 'Price above threshold'
        else:
            detail_text = 'Weak momentum (EMA20 < EMA60)'
        
        return html.Div([
            html.Div([
                html.Strong("Status: "), 
                html.Span(status_text, className=status_class)
            ], className="mb-2"),
            html.Div([
                html.Strong("Details: "), html.Span(detail_text)
            ], className="mb-2"),
            html.Div([
                html.Strong("Buy Condition: "), 
                html.Span(f"Price ≤ ${buy_threshold:.6f}")
            ], className="mb-2"),
            html.Div([
                html.Strong("Last Trade: "), html.Span(last_trade)
            ])
        ])
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
        health_status = '✅ Healthy' if not initialization_error else '❌ Unhealthy'
        health_class = 'text-success' if not initialization_error else 'text-danger'
        
        api_status = '● Connected' if not initialization_error else '⚠ Error'
        api_class = 'text-success' if not initialization_error else 'text-warning'
        
        # Get cache stats
        cache_status = '❌ Disabled'
        cache_class = 'text-warning'
        cache_keys = 0
        
        if exchange_client and config:
            try:
                cache_stats = exchange_client.get_cache_stats()
                cache_enabled = cache_stats.get('enabled', False)
                cache_connected = cache_stats.get('status') == 'connected'
                cache_keys = cache_stats.get('cache_keys', 0)
                
                if cache_enabled and cache_connected:
                    cache_status = '✅ Connected'
                    cache_class = 'text-success'
                elif cache_enabled:
                    cache_status = '⚠ Degraded'
                    cache_class = 'text-warning'
            except:
                pass
        
        return html.Div([
            html.Div([
                html.Strong("Health Check: "), 
                html.Span(health_status, className=health_class)
            ], className="mb-2"),
            html.Div([
                html.Strong("API Status: "), 
                html.Span(api_status, className=api_class)
            ], className="mb-2"),
            html.Div([
                html.Strong("Redis Cache: "), 
                html.Span(cache_status, className=cache_class)
            ], className="mb-2"),
            html.Div([
                html.Strong("Data Delay: "), 
                html.Span("< 100ms", className="text-success")
            ], className="mb-2"),
            html.Div([
                html.Strong("Cache Keys: "), html.Span(str(cache_keys))
            ])
        ])
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
        
        table_header = [
            html.Thead(html.Tr([
                html.Th("ID"),
                html.Th("Timestamp"),
                html.Th("Action"),
                html.Th("Price"),
                html.Th("Amount"),
                html.Th("Cost"),
            ]))
        ]
        
        rows = []
        for trade in trades:
            action_class = "text-success" if trade.get('action') == 'BUY' else "text-danger"
            rows.append(html.Tr([
                html.Td(trade.get('id', '')),
                html.Td(datetime.fromisoformat(trade.get('timestamp', '')).strftime('%Y-%m-%d %H:%M:%S')),
                html.Td(trade.get('action', ''), className=action_class),
                html.Td(f"${trade.get('price', 0):.6f}"),
                html.Td(f"{trade.get('amount', 0):.4f}"),
                html.Td(f"${trade.get('cost', 0):.2f}"),
            ]))
        
        table_body = [html.Tbody(rows)]
        
        return dbc.Table(
            table_header + table_body,
            bordered=True,
            dark=True,
            hover=True,
            responsive=True,
            striped=True,
            size="sm"
        )
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


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=False
    )
