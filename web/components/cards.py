"""Card components for displaying data in the dashboard."""
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime
from typing import List, Dict, Any


def create_status_banner(error: str = None) -> dbc.Alert:
    """
    Create status banner alert.
    
    Args:
        error: Error message if system has initialization error
    
    Returns:
        Bootstrap Alert component
    """
    if error:
        return dbc.Alert(
            f"⚠️ System Error: {error}",
            color="danger",
            dismissable=False
        )
    return dbc.Alert(
        "✅ System operational - All services running normally",
        color="success",
        dismissable=False
    )


def create_market_data_card(
    symbol: str,
    price: float,
    change_24h: float,
    ema20: float,
    ema60: float
) -> html.Div:
    """
    Create market data display card content.
    
    Args:
        symbol: Trading symbol
        price: Current price
        change_24h: 24-hour price change percentage
        ema20: EMA20 value
        ema60: EMA60 value
    
    Returns:
        Div element with market data
    """
    change_class = "text-success" if change_24h >= 0 else "text-danger"
    change_symbol = "+" if change_24h >= 0 else ""
    
    return html.Div([
        html.Div([
            html.Strong("Symbol: "),
            html.Span(f"{symbol}")
        ], className="mb-2"),
        html.Div([
            html.Strong("Price: "),
            html.Span(f"${price:.6f}")
        ], className="mb-2"),
        html.Div([
            html.Strong("24H Change: "),
            html.Span(
                f"{change_symbol}{change_24h:.2f}%",
                className=change_class
            )
        ], className="mb-2"),
        html.Div([
            html.Strong("EMA 20: "),
            html.Span(f"${ema20:.6f}")
        ], className="mb-2"),
        html.Div([
            html.Strong("EMA 60: "),
            html.Span(f"${ema60:.6f}")
        ], className="mb-2"),
        html.Div([
            html.Strong("Data Delay: "),
            html.Span("< 1s (Redis)", className="text-success")
        ])
    ])


def create_position_card(
    qrl_balance: float,
    usdt_balance: float,
    current_position: float,
    max_position: float,
    utilization: float
) -> html.Div:
    """
    Create position status card content.
    
    Args:
        qrl_balance: QRL token balance
        usdt_balance: USDT balance
        current_position: Current position value
        max_position: Maximum position limit
        utilization: Position utilization percentage
    
    Returns:
        Div element with position data
    """
    available_capacity = max_position - current_position
    progress_color = (
        "success" if utilization < 80 
        else "warning" if utilization < 95 
        else "danger"
    )
    
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
            html.Span(f"${max_position:.2f}")
        ], className="mb-2"),
        html.Div([
            html.Strong("Available: "),
            html.Span(f"${available_capacity:.2f}")
        ], className="mb-2"),
        html.Div([
            dbc.Progress(
                value=utilization,
                label=f"{utilization:.1f}%",
                color=progress_color,
                className="mb-1"
            )
        ], className="mb-2"),
    ])


def create_strategy_card(
    buy_signal: bool,
    buy_threshold: float,
    price: float,
    ema20: float,
    ema60: float,
    last_trade: str
) -> html.Div:
    """
    Create strategy status card content.
    
    Args:
        buy_signal: Whether buy signal is active
        buy_threshold: Buy threshold price
        price: Current price
        ema20: EMA20 value
        ema60: EMA60 value
        last_trade: Last trade timestamp
    
    Returns:
        Div element with strategy status
    """
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
            html.Strong("Details: "),
            html.Span(detail_text)
        ], className="mb-2"),
        html.Div([
            html.Strong("Buy Condition: "),
            html.Span(f"Price ≤ ${buy_threshold:.6f}")
        ], className="mb-2"),
        html.Div([
            html.Strong("Last Trade: "),
            html.Span(last_trade)
        ])
    ])


def create_system_card(
    health_status: str,
    cache_enabled: bool,
    cache_connected: bool,
    cache_keys: int
) -> html.Div:
    """
    Create system status card content.
    
    Args:
        health_status: System health status
        cache_enabled: Whether cache is enabled
        cache_connected: Whether cache is connected
        cache_keys: Number of cached keys
    
    Returns:
        Div element with system status
    """
    health_text = '✅ Healthy' if health_status == 'healthy' else '❌ Unhealthy'
    health_class = (
        'text-success' if health_status == 'healthy' 
        else 'text-danger'
    )
    
    api_text = '● Connected' if health_status == 'healthy' else '⚠ Error'
    api_class = (
        'text-success' if health_status == 'healthy' 
        else 'text-warning'
    )
    
    if cache_enabled and cache_connected:
        cache_text = '✅ Connected'
        cache_class = 'text-success'
    elif cache_enabled:
        cache_text = '⚠ Degraded'
        cache_class = 'text-warning'
    else:
        cache_text = '❌ Disabled'
        cache_class = 'text-warning'
    
    return html.Div([
        html.Div([
            html.Strong("Health Check: "),
            html.Span(health_text, className=health_class)
        ], className="mb-2"),
        html.Div([
            html.Strong("API Status: "),
            html.Span(api_text, className=api_class)
        ], className="mb-2"),
        html.Div([
            html.Strong("Redis Cache: "),
            html.Span(cache_text, className=cache_class)
        ], className="mb-2"),
        html.Div([
            html.Strong("Data Delay: "),
            html.Span("< 100ms", className="text-success")
        ], className="mb-2"),
        html.Div([
            html.Strong("Cache Keys: "),
            html.Span(str(cache_keys))
        ])
    ])


def create_trade_history_table(trades: List[Dict[str, Any]]) -> dbc.Table:
    """
    Create trade history table.
    
    Args:
        trades: List of trade dictionaries
    
    Returns:
        Bootstrap Table component
    """
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
        action_class = (
            "text-success" if trade.get('action') == 'BUY' 
            else "text-danger"
        )
        timestamp = datetime.fromisoformat(trade.get('timestamp', ''))
        rows.append(html.Tr([
            html.Td(trade.get('id', '')),
            html.Td(timestamp.strftime('%Y-%m-%d %H:%M:%S')),
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
