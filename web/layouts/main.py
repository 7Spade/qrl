"""Main dashboard layout."""
from dash import dcc, html
import dash_bootstrap_components as dbc


def create_dashboard_layout() -> dbc.Container:
    """
    Create the main dashboard layout structure.
    
    Returns:
        Bootstrap Container with complete dashboard layout
    """
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1(
                    "📊 QRL Trading Bot Dashboard",
                    className="text-center mb-4 text-success"
                )
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
                    dbc.CardHeader(
                        "📈 Market Data",
                        className="bg-success text-white"
                    ),
                    dbc.CardBody(id='market-data')
                ], className="mb-3")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        "💼 Position Status",
                        className="bg-info text-white"
                    ),
                    dbc.CardBody(id='position-data')
                ], className="mb-3")
            ], md=6),
        ]),
        
        # Charts row - Price chart with timeframe selector
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
                                style={
                                    'width': '150px',
                                    'display': 'inline-block'
                                }
                            )
                        ], style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'space-between'
                        })
                    ], className="bg-primary text-white"),
                    dbc.CardBody([
                        dcc.Graph(
                            id='price-chart',
                            style={'height': '400px'}
                        )
                    ])
                ], className="mb-3")
            ], md=12),
        ]),
        
        # Indicators row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        "📉 Technical Indicators",
                        className="bg-warning text-dark"
                    ),
                    dbc.CardBody([
                        dcc.Graph(
                            id='indicators-chart',
                            style={'height': '400px'}
                        )
                    ])
                ], className="mb-3")
            ], md=12),
        ]),
        
        # Bottom row - Strategy and System
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        "🎯 Strategy Status",
                        className="bg-success text-white"
                    ),
                    dbc.CardBody(id='strategy-data')
                ], className="mb-3")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        "⚙️ System Status",
                        className="bg-secondary text-white"
                    ),
                    dbc.CardBody(id='system-data')
                ], className="mb-3")
            ], md=6),
        ]),
        
        # Trade History
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        "📜 Recent Trades",
                        className="bg-info text-white"
                    ),
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
                    html.P(
                        "Last Updated: ",
                        className="text-muted d-inline"
                    ),
                    html.Span(id='last-update', className="text-info")
                ], className="text-center")
            ])
        ])
    ], fluid=True)
