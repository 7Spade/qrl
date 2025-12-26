"""Card components for displaying data in the dashboard."""
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime
from typing import List, Dict, Any


def create_featured_price_card(
    symbol: str,
    price: float,
    change_24h: float,
    high_24h: float,
    low_24h: float,
    volume_24h: float
) -> html.Div:
    """
    Create a large, prominent featured price display card.
    
    Args:
        symbol: Trading symbol
        price: Current price
        change_24h: 24-hour price change percentage
        high_24h: 24-hour high price
        low_24h: 24-hour low price
        volume_24h: 24-hour volume
    
    Returns:
        Div element with featured price display
    """
    change_class = "success" if change_24h >= 0 else "danger"
    change_symbol = "▲" if change_24h >= 0 else "▼"
    trend_icon = "fa-arrow-trend-up" if change_24h >= 0 else "fa-arrow-trend-down"
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2(symbol.replace("/", " / "), 
                           className="mb-2 fw-bold",
                           style={'color': 'white', 'font-size': '2.5rem'}),
                    html.Div([
                        html.Span(f"${price:.6f}", 
                                 style={
                                     'font-size': '4rem',
                                     'font-weight': 'bold',
                                     'color': 'white',
                                     'line-height': '1'
                                 }),
                        html.Div([
                            html.I(className=f"fas {trend_icon} me-2"),
                            html.Span(f"{change_symbol} {abs(change_24h):.2f}%",
                                     style={'font-size': '1.5rem'})
                        ], className=f"text-{change_class} mt-2",
                           style={'font-weight': '600'})
                    ])
                ])
            ], md=6),
            dbc.Col([
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.P("24H High", 
                                      className="mb-1 text-white-50",
                                      style={'font-size': '0.9rem'}),
                                html.H4(f"${high_24h:.6f}",
                                       className="mb-0 text-success fw-bold")
                            ], className="text-center p-3")
                        ], md=6),
                        dbc.Col([
                            html.Div([
                                html.P("24H Low", 
                                      className="mb-1 text-white-50",
                                      style={'font-size': '0.9rem'}),
                                html.H4(f"${low_24h:.6f}",
                                       className="mb-0 text-danger fw-bold")
                            ], className="text-center p-3")
                        ], md=6),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.P("24H Volume", 
                                      className="mb-1 text-white-50",
                                      style={'font-size': '0.9rem'}),
                                html.H4(f"${volume_24h:,.0f}",
                                       className="mb-0 text-info fw-bold")
                            ], className="text-center p-3")
                        ], md=12),
                    ])
                ], style={
                    'background': 'rgba(255, 255, 255, 0.1)',
                    'border-radius': '10px',
                    'padding': '10px'
                })
            ], md=6)
        ])
    ])


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
            html.Div([
                html.Span("Symbol", className="text-muted", style={'font-size': '0.85rem'}),
                html.Div(f"{symbol}", className="fw-bold", style={'font-size': '1.2rem'})
            ], className="mb-3 p-3", style={
                'background': 'rgba(102, 126, 234, 0.1)',
                'border-radius': '10px'
            }),
        ]),
        html.Div([
            html.Div([
                html.Span("Current Price", className="text-muted", style={'font-size': '0.85rem'}),
                html.Div(f"${price:.6f}", className="fw-bold text-info", style={'font-size': '1.3rem'})
            ], className="mb-3 p-3", style={
                'background': 'rgba(52, 152, 219, 0.1)',
                'border-radius': '10px'
            }),
        ]),
        html.Div([
            html.Div([
                html.Span("24H Change", className="text-muted", style={'font-size': '0.85rem'}),
                html.Div(
                    f"{change_symbol}{change_24h:.2f}%",
                    className=f"fw-bold {change_class}",
                    style={'font-size': '1.2rem'}
                )
            ], className="mb-3 p-3", style={
                'background': 'rgba(255, 255, 255, 0.05)',
                'border-radius': '10px'
            }),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("EMA 20", className="text-muted", style={'font-size': '0.85rem'}),
                    html.Div(f"${ema20:.6f}", className="fw-bold text-success", style={'font-size': '1.1rem'})
                ], className="p-3 text-center", style={
                    'background': 'rgba(17, 153, 142, 0.1)',
                    'border-radius': '10px'
                })
            ], md=6),
            dbc.Col([
                html.Div([
                    html.Span("EMA 60", className="text-muted", style={'font-size': '0.85rem'}),
                    html.Div(f"${ema60:.6f}", className="fw-bold text-warning", style={'font-size': '1.1rem'})
                ], className="p-3 text-center", style={
                    'background': 'rgba(245, 87, 108, 0.1)',
                    'border-radius': '10px'
                })
            ], md=6),
        ], className="mb-3"),
        html.Div([
            html.I(className="fas fa-database me-2 text-success"),
            html.Span("Data Delay: < 1s (Redis)", className="text-success", style={'font-size': '0.85rem'})
        ], className="text-center")
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
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-coins me-2 text-warning"),
                        html.Span("QRL", className="text-muted", style={'font-size': '0.85rem'})
                    ]),
                    html.Div(f"{qrl_balance:.4f}", 
                            className="fw-bold text-warning mt-1", 
                            style={'font-size': '1.3rem'})
                ], className="p-3 text-center", style={
                    'background': 'rgba(255, 193, 7, 0.1)',
                    'border-radius': '10px'
                })
            ], md=6),
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-dollar-sign me-2 text-success"),
                        html.Span("USDT", className="text-muted", style={'font-size': '0.85rem'})
                    ]),
                    html.Div(f"{usdt_balance:.2f}", 
                            className="fw-bold text-success mt-1", 
                            style={'font-size': '1.3rem'})
                ], className="p-3 text-center", style={
                    'background': 'rgba(17, 153, 142, 0.1)',
                    'border-radius': '10px'
                })
            ], md=6),
        ], className="mb-3"),
        html.Div([
            html.Div([
                html.Span("Current Position", className="text-muted", style={'font-size': '0.85rem'}),
                html.Div(f"${current_position:.2f}", 
                        className="fw-bold text-info", 
                        style={'font-size': '1.2rem'})
            ], className="mb-2")
        ], className="p-3", style={
            'background': 'rgba(52, 152, 219, 0.1)',
            'border-radius': '10px'
        }),
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Max Position", className="text-muted me-2", style={'font-size': '0.85rem'}),
                    html.Span(f"${max_position:.2f}", className="fw-bold")
                ], className="mb-2"),
                html.Div([
                    html.Span("Available", className="text-success me-2", style={'font-size': '0.85rem'}),
                    html.Span(f"${available_capacity:.2f}", className="fw-bold text-success")
                ], className="mb-3")
            ])
        ], className="p-3 mb-3", style={
            'background': 'rgba(255, 255, 255, 0.05)',
            'border-radius': '10px'
        }),
        html.Div([
            html.Div("Position Utilization", className="text-muted mb-2", style={'font-size': '0.9rem'}),
            dbc.Progress(
                value=utilization,
                label=f"{utilization:.1f}%",
                color=progress_color,
                className="mb-1",
                style={'height': '30px', 'font-size': '1.1rem', 'font-weight': 'bold'}
            )
        ])
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
    status_class = 'success' if buy_signal else 'warning'
    status_bg = 'rgba(17, 153, 142, 0.2)' if buy_signal else 'rgba(255, 193, 7, 0.2)'
    
    if buy_signal:
        detail_text = 'Conditions met - Ready to execute'
        detail_icon = 'fa-check-circle'
        detail_class = 'text-success'
    elif price > buy_threshold:
        if ema20 < ema60:
            detail_text = 'Price too high & Momentum weak'
            detail_icon = 'fa-times-circle'
            detail_class = 'text-danger'
        else:
            detail_text = 'Price above threshold'
            detail_icon = 'fa-exclamation-circle'
            detail_class = 'text-warning'
    else:
        detail_text = 'Weak momentum (EMA20 < EMA60)'
        detail_icon = 'fa-info-circle'
        detail_class = 'text-info'
    
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=f"fas fa-chart-line me-2"),
                html.Span("Status", className="text-muted", style={'font-size': '0.85rem'})
            ]),
            html.Div(status_text, 
                    className=f"fw-bold text-{status_class} mt-2", 
                    style={'font-size': '1.5rem'})
        ], className="p-3 mb-3 text-center", style={
            'background': status_bg,
            'border-radius': '10px'
        }),
        html.Div([
            html.Div([
                html.I(className=f"fas {detail_icon} me-2 {detail_class}"),
                html.Span(detail_text, className=detail_class, style={'font-size': '0.95rem'})
            ])
        ], className="p-3 mb-3", style={
            'background': 'rgba(255, 255, 255, 0.05)',
            'border-radius': '10px'
        }),
        html.Div([
            html.Div([
                html.Span("Buy Condition", className="text-muted", style={'font-size': '0.85rem'}),
                html.Div(f"Price ≤ ${buy_threshold:.6f}", 
                        className="fw-bold text-info", 
                        style={'font-size': '1.1rem'})
            ])
        ], className="p-3 mb-3", style={
            'background': 'rgba(52, 152, 219, 0.1)',
            'border-radius': '10px'
        }),
        html.Div([
            html.I(className="fas fa-clock me-2 text-muted"),
            html.Span("Last Trade: ", className="text-muted", style={'font-size': '0.85rem'}),
            html.Span(last_trade, className="fw-bold")
        ], className="text-center")
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
        'success' if health_status == 'healthy' 
        else 'danger'
    )
    health_bg = (
        'rgba(17, 153, 142, 0.2)' if health_status == 'healthy'
        else 'rgba(220, 53, 69, 0.2)'
    )
    
    api_text = '● Connected' if health_status == 'healthy' else '⚠ Error'
    api_class = (
        'text-success' if health_status == 'healthy' 
        else 'text-warning'
    )
    
    if cache_enabled and cache_connected:
        cache_text = '✅ Connected'
        cache_class = 'text-success'
        cache_bg = 'rgba(17, 153, 142, 0.1)'
    elif cache_enabled:
        cache_text = '⚠ Degraded'
        cache_class = 'text-warning'
        cache_bg = 'rgba(255, 193, 7, 0.1)'
    else:
        cache_text = '❌ Disabled'
        cache_class = 'text-warning'
        cache_bg = 'rgba(220, 53, 69, 0.1)'
    
    return html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-heartbeat me-2"),
                html.Span("Health Check", className="text-muted", style={'font-size': '0.85rem'})
            ]),
            html.Div(health_text, 
                    className=f"fw-bold text-{health_class} mt-2", 
                    style={'font-size': '1.4rem'})
        ], className="p-3 mb-3 text-center", style={
            'background': health_bg,
            'border-radius': '10px'
        }),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-plug me-2"),
                    html.Span("API", className="text-muted d-block", style={'font-size': '0.75rem'}),
                    html.Span(api_text, className=f"{api_class} fw-bold", style={'font-size': '0.95rem'})
                ], className="p-3 text-center", style={
                    'background': 'rgba(255, 255, 255, 0.05)',
                    'border-radius': '10px'
                })
            ], md=6),
            dbc.Col([
                html.Div([
                    html.I(className="fas fa-database me-2"),
                    html.Span("Redis", className="text-muted d-block", style={'font-size': '0.75rem'}),
                    html.Span(cache_text, className=f"{cache_class} fw-bold", style={'font-size': '0.95rem'})
                ], className="p-3 text-center", style={
                    'background': cache_bg,
                    'border-radius': '10px'
                })
            ], md=6),
        ], className="mb-3"),
        html.Div([
            html.Div([
                html.I(className="fas fa-tachometer-alt me-2 text-success"),
                html.Span("Data Delay: ", className="text-muted", style={'font-size': '0.85rem'}),
                html.Span("< 100ms", className="text-success fw-bold")
            ], className="mb-2"),
            html.Div([
                html.I(className="fas fa-key me-2 text-info"),
                html.Span("Cache Keys: ", className="text-muted", style={'font-size': '0.85rem'}),
                html.Span(str(cache_keys), className="fw-bold")
            ])
        ], className="p-3 text-center", style={
            'background': 'rgba(255, 255, 255, 0.05)',
            'border-radius': '10px'
        })
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
