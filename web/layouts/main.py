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
        # Modern Header with Gradient
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1(
                        "🚀 QRL Trading Bot",
                        className="text-center mb-2",
                        style={
                            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            '-webkit-background-clip': 'text',
                            '-webkit-text-fill-color': 'transparent',
                            'font-weight': 'bold',
                            'font-size': '3rem'
                        }
                    ),
                    html.P(
                        "Real-time QRL/USDT Trading Dashboard",
                        className="text-center text-muted mb-4",
                        style={'font-size': '1.1rem'}
                    )
                ], style={
                    'padding': '20px',
                    'border-radius': '15px',
                    'background': 'rgba(102, 126, 234, 0.05)',
                    'margin-bottom': '20px'
                })
            ])
        ]),
        
        # Status banner
        dbc.Row([
            dbc.Col([
                html.Div(id='status-banner', className="mb-3")
            ])
        ]),
        
        # Featured Price Card - Prominent QRL Price Display
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id='featured-price-card')
                    ], style={'padding': '30px'})
                ], className="mb-4", style={
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'border': 'none',
                    'border-radius': '20px',
                    'box-shadow': '0 10px 30px rgba(102, 126, 234, 0.3)'
                })
            ], md=12),
        ]),
        
        # Top row - Market Data and Position with Modern Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-chart-line me-2"),
                            html.Span("Market Data")
                        ])
                    ], style={
                        'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '15px 15px 0 0',
                        'padding': '15px'
                    }),
                    dbc.CardBody(id='market-data')
                ], className="mb-3", style={
                    'border': 'none',
                    'border-radius': '15px',
                    'box-shadow': '0 5px 15px rgba(17, 153, 142, 0.2)'
                })
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-wallet me-2"),
                            html.Span("Position Status")
                        ])
                    ], style={
                        'background': 'linear-gradient(135deg, #3498db 0%, #2c3e50 100%)',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '15px 15px 0 0',
                        'padding': '15px'
                    }),
                    dbc.CardBody(id='position-data')
                ], className="mb-3", style={
                    'border': 'none',
                    'border-radius': '15px',
                    'box-shadow': '0 5px 15px rgba(52, 152, 219, 0.2)'
                })
            ], md=6),
        ]),
        
        # Charts row - Price chart with timeframe selector (Modern Design)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-chart-area me-2"),
                                "Price Chart"
                            ], className="me-3", style={'font-weight': '600'}),
                            dcc.Dropdown(
                                id='timeframe-selector',
                                options=[
                                    {'label': '📊 1 Minute', 'value': '1m'},
                                    {'label': '📊 5 Minutes', 'value': '5m'},
                                    {'label': '📊 15 Minutes', 'value': '15m'},
                                    {'label': '📊 30 Minutes', 'value': '30m'},
                                    {'label': '📊 1 Hour', 'value': '1h'},
                                    {'label': '📊 4 Hours', 'value': '4h'},
                                    {'label': '📊 1 Day', 'value': '1d'},
                                ],
                                value='1h',
                                clearable=False,
                                style={
                                    'width': '180px',
                                    'display': 'inline-block'
                                }
                            )
                        ], style={
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'space-between'
                        })
                    ], style={
                        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '15px 15px 0 0',
                        'padding': '15px'
                    }),
                    dbc.CardBody([
                        dcc.Graph(
                            id='price-chart',
                            style={'height': '450px'}
                        )
                    ])
                ], className="mb-3", style={
                    'border': 'none',
                    'border-radius': '15px',
                    'box-shadow': '0 5px 15px rgba(102, 126, 234, 0.2)'
                })
            ], md=12),
        ]),
        
        # Indicators row (Modern Design)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-line me-2"),
                        html.Span("Technical Indicators")
                    ], style={
                        'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '15px 15px 0 0',
                        'padding': '15px',
                        'font-weight': '600'
                    }),
                    dbc.CardBody([
                        dcc.Graph(
                            id='indicators-chart',
                            style={'height': '450px'}
                        )
                    ])
                ], className="mb-3", style={
                    'border': 'none',
                    'border-radius': '15px',
                    'box-shadow': '0 5px 15px rgba(240, 147, 251, 0.2)'
                })
            ], md=12),
        ]),
        
        # Bottom row - Strategy and System (Modern Design)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-bullseye me-2"),
                        html.Span("Strategy Status")
                    ], style={
                        'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '15px 15px 0 0',
                        'padding': '15px',
                        'font-weight': '600'
                    }),
                    dbc.CardBody(id='strategy-data')
                ], className="mb-3", style={
                    'border': 'none',
                    'border-radius': '15px',
                    'box-shadow': '0 5px 15px rgba(17, 153, 142, 0.2)'
                })
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-cog me-2"),
                        html.Span("System Status")
                    ], style={
                        'background': 'linear-gradient(135deg, #434343 0%, #000000 100%)',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '15px 15px 0 0',
                        'padding': '15px',
                        'font-weight': '600'
                    }),
                    dbc.CardBody(id='system-data')
                ], className="mb-3", style={
                    'border': 'none',
                    'border-radius': '15px',
                    'box-shadow': '0 5px 15px rgba(67, 67, 67, 0.2)'
                })
            ], md=6),
        ]),
        
        # Trade History (Modern Design)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-history me-2"),
                        html.Span("Recent Trades")
                    ], style={
                        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '15px 15px 0 0',
                        'padding': '15px',
                        'font-weight': '600'
                    }),
                    dbc.CardBody(id='trade-history')
                ], className="mb-3", style={
                    'border': 'none',
                    'border-radius': '15px',
                    'box-shadow': '0 5px 15px rgba(102, 126, 234, 0.2)'
                })
            ], md=12),
        ]),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # Update every 60 seconds
            n_intervals=0
        ),
        
        # Modern Footer
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P([
                        html.I(className="fas fa-sync-alt me-2"),
                        "Last Updated: ",
                        html.Span(id='last-update', className="text-info fw-bold")
                    ], className="text-muted text-center mb-0")
                ], style={
                    'padding': '15px',
                    'border-radius': '10px',
                    'background': 'rgba(102, 126, 234, 0.05)',
                    'margin-top': '10px'
                })
            ])
        ])
    ], fluid=True, style={'background': '#0a0e27', 'min-height': '100vh', 'padding': '20px'})
