# Dash Dashboard Architecture

## Overview

The QRL Trading Bot dashboard uses a modular Dash architecture to reduce cognitive load and improve maintainability. The 700+ line monolithic `dash_app.py` has been refactored into focused, reusable components.

## Directory Structure

```
web/
├── __init__.py              # Package initialization
├── app.py                   # Main entry point (62 lines)
├── callbacks/               # Callback modules
│   ├── __init__.py
│   ├── chart_callbacks.py   # Chart update callbacks (87 lines)
│   └── data_callbacks.py    # Data update callbacks (177 lines)
├── components/              # Reusable UI components
│   ├── __init__.py
│   ├── cards.py             # Card components (264 lines)
│   └── charts.py            # Chart components (204 lines)
└── layouts/                 # Layout definitions
    ├── __init__.py
    └── main.py              # Main dashboard layout (162 lines)
```

## Architecture Benefits

### 1. Separation of Concerns
- **Components** (`components/`): Reusable UI elements
- **Layouts** (`layouts/`): Page structure and arrangement
- **Callbacks** (`callbacks/`): Business logic and data updates
- **App** (`app.py`): Assembly and initialization

### 2. Reduced Cognitive Load
- Each module is focused on a single responsibility
- Files are 62-264 lines vs. the original 719 lines
- Easy to locate and modify specific functionality

### 3. Reusability
- Components can be used across different layouts
- Callbacks are modular and testable
- Charts are configurable and reusable

### 4. Maintainability
- Changes to UI don't affect business logic
- New features can be added without modifying existing code
- Clear dependency flow

## Component Modules

### `components/charts.py`
Provides chart creation functions:
- `create_price_chart()`: Candlestick chart with MA/EMA overlays
- `create_indicators_chart()`: Technical indicators (Williams %R, RSI, MACD)
- `calculate_indicators()`: Indicator calculation helper

**Usage:**
```python
from web.components.charts import create_price_chart, calculate_indicators

df = calculate_indicators(ohlcv_df)
fig = create_price_chart(df, symbol="QRL/USDT")
```

### `components/cards.py`
Provides card content generators:
- `create_status_banner()`: System status alert
- `create_market_data_card()`: Market data display
- `create_position_card()`: Position tracking
- `create_strategy_card()`: Strategy status
- `create_system_card()`: System health
- `create_trade_history_table()`: Trade history table

**Usage:**
```python
from web.components.cards import create_market_data_card

content = create_market_data_card(
    symbol="QRL/USDT",
    price=0.123456,
    change_24h=5.2,
    ema20=0.120000,
    ema60=0.118000
)
```

## Layout Modules

### `layouts/main.py`
Defines the complete dashboard structure:
- Header with title
- Status banner area
- Market data and position cards (2-column row)
- Price chart with timeframe selector
- Technical indicators chart
- Strategy and system status cards (2-column row)
- Trade history table
- Auto-refresh interval component
- Footer with timestamp

**Usage:**
```python
from web.layouts.main import create_dashboard_layout

app.layout = create_dashboard_layout()
```

## Callback Modules

### `callbacks/data_callbacks.py`
Registers data update callbacks:
- `update_status_banner()`: System status
- `update_market_data()`: Market prices and EMAs
- `update_position_data()`: Position and balances
- `update_strategy_data()`: Strategy signals
- `update_system_data()`: System health
- `update_trade_history()`: Recent trades
- `update_timestamp()`: Last update time

**Usage:**
```python
from web.callbacks import data_callbacks

data_callbacks.register_callbacks(
    app, config, state_manager, exchange_client, initialization_error
)
```

### `callbacks/chart_callbacks.py`
Registers chart update callbacks:
- `update_price_chart()`: Price candlestick chart
- `update_indicators_chart()`: Technical indicators

**Usage:**
```python
from web.callbacks import chart_callbacks

chart_callbacks.register_callbacks(app, config, exchange_client)
```

## Main Application (`app.py`)

The main entry point assembles all components:

```python
# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Initialize services
config = AppConfig.load()
state_manager = StateManager()
exchange_client = ExchangeClient(...)

# Set layout
app.layout = create_dashboard_layout()

# Register callbacks
data_callbacks.register_callbacks(app, config, state_manager, ...)
chart_callbacks.register_callbacks(app, config, exchange_client)

# Run server
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080)
```

## Adding New Features

### Add a New Card Component
1. Create function in `components/cards.py`
2. Use in layout from `layouts/main.py`
3. Register callback in `callbacks/data_callbacks.py`

### Add a New Chart
1. Create function in `components/charts.py`
2. Add to layout with `dcc.Graph` in `layouts/main.py`
3. Register callback in `callbacks/chart_callbacks.py`

### Add a New Page (Multi-page App)
1. Create new layout in `layouts/new_page.py`
2. Use `dcc.Location` and callback for routing
3. Register page-specific callbacks

## Testing Components

Each module can be tested independently:

```python
# Test chart component
from web.components.charts import calculate_indicators
import pandas as pd

df = pd.DataFrame(ohlcv_data)
df = calculate_indicators(df)
assert 'ema20' in df.columns
assert 'rsi' in df.columns
```

## Performance Considerations

- **Callbacks are independent**: Each callback runs separately
- **Shared data sources**: All callbacks use the same client instances
- **Auto-refresh**: 60-second interval prevents excessive API calls
- **Lazy imports**: Only import what's needed in each module

## Migration from Monolithic to Modular

**Before** (719 lines in one file):
- Hard to navigate
- Mixed concerns (UI, logic, data)
- Difficult to test individual parts

**After** (6 focused modules):
- Clear structure
- Easy to locate functionality
- Testable components
- Reusable across pages

## Best Practices

1. **Keep components pure**: Accept data as parameters, return UI elements
2. **Register callbacks separately**: Don't mix callback logic with components
3. **Use type hints**: Improve code clarity and IDE support
4. **Document functions**: Clear docstrings for all public functions
5. **Consistent naming**: `create_*` for components, `update_*` for callbacks

## Production Deployment

### Local Development
For local development, run the app directly with Python:
```bash
python web/app.py
# Runs on http://localhost:8080
```

### Production (Cloud Run / Docker)
For production deployment, the app uses Gunicorn for better performance and reliability:
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 web.app:server
```

**Configuration:**
- `workers=1`: Single worker process (sufficient for Dash apps)
- `threads=8`: Multiple threads for handling concurrent requests
- `timeout=0`: No timeout (important for long-running callbacks)
- `web.app:server`: References the Flask server instance

### Health Check Endpoint
The app includes a `/health` endpoint for Cloud Run health checks:
```bash
curl http://localhost:8080/health
# Returns: {"status": "healthy", "service": "qrl-bot", "version": "2.0.0"}
```

This endpoint reports system health even if component initialization fails, allowing the container to start successfully.

### Troubleshooting Cloud Run Deployment

**Issue: Container failed to start**
- Check that gunicorn is in `requirements.txt`
- Verify PORT environment variable is properly set
- Review logs for initialization errors
- Ensure health endpoint responds within timeout

**Issue: Callbacks not working**
- Verify all callback dependencies are initialized
- Check that callbacks handle None values gracefully
- Review browser console for errors
