"""
Modular Dash-based web dashboard for QRL trading bot.

This is the main entry point that assembles components, layouts, and callbacks
into a cohesive dashboard application.

Usage:
    python web/app.py
"""
import logging
import os

import dash
import dash_bootstrap_components as dbc

from src.core.config import AppConfig
from src.data.state import StateManager
from src.data.exchange import ExchangeClient
from src.strategies.ema_strategy import EMAAccumulationStrategy

from web.layouts.main import create_dashboard_layout
from web.callbacks import data_callbacks, chart_callbacks

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
config = None
state_manager = None
exchange_client = None
strategy = None

try:
    config = AppConfig.load()
    state_manager = StateManager()
    exchange_client = ExchangeClient(config.exchange, cache_config=config.cache)
    strategy = EMAAccumulationStrategy()
    logger.info("✅ All components initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize components: {e}")
    initialization_error = str(e)

# Set app layout
app.layout = create_dashboard_layout()

# Register all callbacks
data_callbacks.register_callbacks(
    app, config, state_manager, exchange_client, initialization_error
)
chart_callbacks.register_callbacks(app, config, exchange_client)

# Server instance for deployment
server = app.server

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run_server(
        host='0.0.0.0',
        port=port,
        debug=False
    )
