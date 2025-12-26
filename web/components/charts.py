"""Chart components for the Dash dashboard."""
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional


def create_price_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create candlestick price chart with moving averages.
    
    Args:
        df: DataFrame with OHLCV data and calculated indicators
        symbol: Trading symbol for chart title
    
    Returns:
        Plotly Figure with candlestick and MA/EMA overlays
    """
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
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=30, b=50)
    )
    
    return fig


def create_indicators_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create technical indicators chart with subplots.
    
    Args:
        df: DataFrame with calculated technical indicators
    
    Returns:
        Plotly Figure with Williams %R, RSI, and MACD subplots
    """
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
        marker_color=['green' if val > 0 else 'red' 
                     for val in df['macd_histogram']]
    ), row=3, col=1)
    
    fig.update_layout(
        template='plotly_dark',
        showlegend=True,
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(title_text="Time", row=3, col=1)
    
    return fig


def calculate_indicators(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate technical indicators for the given DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for indicator calculations
    
    Returns:
        DataFrame with calculated indicators
    """
    # Calculate moving averages
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma60'] = df['close'].rolling(window=60).mean()
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema60'] = df['close'].ewm(span=60, adjust=False).mean()
    
    # Williams %R
    df['highest_high'] = df['high'].rolling(window=period).max()
    df['lowest_low'] = df['low'].rolling(window=period).min()
    df['williams_r'] = (
        (df['highest_high'] - df['close']) / 
        (df['highest_high'] - df['lowest_low'])
    ) * -100
    
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
    
    return df
