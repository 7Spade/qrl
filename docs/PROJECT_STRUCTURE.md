# Project Structure Documentation

## Overview

This document explains the new modular structure of the QRL trading bot (v2.0).

## Directory Layout

```
qrl/
├── src/                           # Source code (modular architecture)
│   ├── __init__.py               # Package marker
│   ├── core/                     # Core orchestration
│   │   ├── __init__.py
│   │   ├── config.py             # Centralized configuration
│   │   └── engine.py             # Trading engine (main orchestrator)
│   ├── strategies/               # Trading strategies
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract strategy interface
│   │   └── ema_strategy.py       # EMA accumulation strategy
│   ├── risk/                     # Risk management
│   │   ├── __init__.py
│   │   └── manager.py            # Risk checks and limits
│   ├── execution/                # Order execution
│   │   ├── __init__.py
│   │   └── order_manager.py      # Order placement and tracking
│   ├── data/                     # Data layer
│   │   ├── __init__.py
│   │   ├── exchange.py           # Exchange API client
│   │   └── state.py              # State and trade history
│   └── monitoring/               # Logging and alerts
│       ├── __init__.py
│       └── logger.py             # Structured logging
├── web/                          # Web dashboard
│   ├── app.py                    # Original FastAPI app (v1.0)
│   ├── app_new.py                # Enhanced FastAPI app (v2.0)
│   └── templates/
│       ├── index.html            # Original dashboard
│       └── dashboard.html        # Enhanced dashboard
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── test_strategy.py      # Strategy tests
│   │   └── test_risk.py          # Risk management tests
│   └── integration/              # Integration tests (future)
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # Architecture overview
│   ├── MIGRATION_GUIDE.md        # v1 → v2 migration
│   ├── PROJECT_STRUCTURE.md      # This file
│   ├── 交易機器人完整規範指南.md    # Complete specification
│   └── 交易機器人頁面指南.md        # Page implementation guide
├── data/                         # Data storage (gitignored)
│   └── state.db                  # SQLite database
├── logs/                         # Log files (gitignored)
│   └── trading.log               # Application logs
├── main.py                       # Original entry point (v1.0)
├── main_new.py                   # New entry point (v2.0)
├── config.py                     # Legacy config (v1.0)
├── exchange.py                   # Legacy exchange (v1.0)
├── strategy.py                   # Legacy strategy (v1.0)
├── risk.py                       # Legacy risk (v1.0)
├── state.py                      # Legacy state (v1.0)
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── Dockerfile                    # Docker configuration
└── cloudbuild.yaml               # Cloud Build config
```

## Module Responsibilities

### `src/core/` - Core Orchestration

**Purpose**: Central coordination and configuration

**Files**:
- `config.py`: Pydantic-based configuration with validation
- `engine.py`: Trading engine that orchestrates all components

**Key Classes**:
- `AppConfig`: Complete application configuration
- `TradingConfig`: Trading parameters (symbol, order size, limits)
- `ExchangeConfig`: Exchange API credentials
- `MonitoringConfig`: Logging and alerting settings
- `TradingEngine`: Main orchestrator

**Usage**:
```python
from src.core.config import AppConfig
from src.core.engine import TradingEngine

config = AppConfig.load()
engine = TradingEngine(config)
engine.execute_trading_cycle()
```

### `src/strategies/` - Trading Strategies

**Purpose**: Signal generation and trading logic

**Files**:
- `base.py`: Abstract base class for all strategies
- `ema_strategy.py`: EMA-based accumulation strategy

**Key Classes**:
- `BaseStrategy`: Abstract interface
- `StrategySignal`: Typed signal output
- `EMAAccumulationStrategy`: Concrete implementation

**Usage**:
```python
from src.strategies.ema_strategy import EMAAccumulationStrategy

strategy = EMAAccumulationStrategy()
signal = strategy.analyze(ohlcv_data)
if signal.should_buy:
    print(f"Buy signal! Price: {signal.metadata['price']}")
```

**Adding New Strategies**:
1. Create new file in `src/strategies/`
2. Extend `BaseStrategy`
3. Implement `analyze()` and `get_required_candles()`
4. Return `StrategySignal`

### `src/risk/` - Risk Management

**Purpose**: Multi-layer risk controls and validation

**Files**:
- `manager.py`: Risk check implementation

**Key Classes**:
- `RiskManager`: Multi-layer risk checks
- `RiskCheck`: Typed check result

**Usage**:
```python
from src.risk.manager import RiskManager

risk = RiskManager(max_position_usdt=500, max_order_usdt=50)
check = risk.can_place_order(current_position=100, order_size=50)
if check.passed:
    print("Risk check passed!")
else:
    print(f"Risk check failed: {check.reason}")
```

### `src/execution/` - Order Execution

**Purpose**: Order placement and tracking

**Files**:
- `order_manager.py`: Order execution logic

**Key Classes**:
- `OrderManager`: Order placement wrapper
- `OrderResult`: Typed execution result

**Usage**:
```python
from src.execution.order_manager import OrderManager
from src.data.exchange import ExchangeClient

exchange = ExchangeClient(config.exchange)
manager = OrderManager(exchange)
result = manager.place_limit_buy("QRL/USDT", 100, 0.45)
if result.success:
    print(f"Order placed! ID: {result.order_id}")
```

### `src/data/` - Data Layer

**Purpose**: Data persistence and exchange integration

**Files**:
- `exchange.py`: Exchange API wrapper
- `state.py`: SQLite state management

**Key Classes**:
- `ExchangeClient`: CCXT wrapper with error handling
- `StateManager`: Position and trade tracking
- `Position`: SQLAlchemy model for position
- `Trade`: SQLAlchemy model for trades

**Usage**:
```python
# Exchange client
from src.data.exchange import ExchangeClient
client = ExchangeClient(config.exchange)
ticker = client.fetch_ticker("QRL/USDT")

# State management
from src.data.state import StateManager
state = StateManager()
position = state.get_position()
state.add_trade("BUY", "QRL/USDT", 0.45, 111, 50)
history = state.get_trade_history(limit=10)
```

### `src/monitoring/` - Logging & Alerts

**Purpose**: Structured logging and observability

**Files**:
- `logger.py`: Structured logger implementation

**Key Classes**:
- `StructuredLogger`: JSON-formatted logging

**Usage**:
```python
from src.monitoring.logger import get_logger

logger = get_logger("MyModule")
logger.info("Operation completed", {"key": "value"})
logger.trade("BUY", "QRL/USDT", 0.45, 111, 50)
logger.strategy_signal("EMA", "BUY", {"price": 0.45})
```

### `web/` - Web Dashboard

**Purpose**: Real-time monitoring and visualization

**Files**:
- `app_new.py`: Enhanced FastAPI application
- `templates/dashboard.html`: Improved UI

**Endpoints**:
- `GET /`: Main dashboard
- `GET /health`: Health check
- `GET /api/trades`: Trade history
- `GET /api/statistics`: Performance stats
- `GET /api/logs`: System logs
- `GET /api/market`: Market data with indicators

**Usage**:
```bash
python web/dash_app.py
```

### `tests/` - Test Suite

**Purpose**: Automated testing

**Structure**:
- `unit/`: Unit tests for individual components
- `integration/`: Integration tests (future)

**Running Tests**:
```bash
pytest tests/
pytest tests/unit/test_strategy.py -v
pytest tests/ --cov=src --cov-report=term-missing
```

## Data Flow

### Trading Cycle

```
1. main_new.py
   ↓
2. TradingEngine.execute_trading_cycle()
   ↓
3. ExchangeClient.fetch_ohlcv()
   ↓
4. EMAAccumulationStrategy.analyze() → StrategySignal
   ↓
5. RiskManager.can_place_order() → RiskCheck
   ↓
6. OrderManager.place_limit_buy() → OrderResult
   ↓
7. StateManager.update_position() + add_trade()
   ↓
8. StructuredLogger.trade()
```

### Web Dashboard Flow

```
1. Browser → GET /
   ↓
2. app_new.py: dashboard()
   ↓
3. ExchangeClient.fetch_ticker() + fetch_ohlcv()
   ↓
4. EMAAccumulationStrategy.analyze()
   ↓
5. StateManager.get_position()
   ↓
6. Jinja2 template rendering
   ↓
7. HTML response → Browser
```

## Configuration Files

### `pyproject.toml`

Defines project metadata, dependencies, and tool configuration:
- Project name, version, dependencies
- Black formatting rules
- Flake8 linting rules
- MyPy type checking
- Pytest configuration

### `requirements.txt`

Python package dependencies:
- Core: ccxt, pandas, numpy, ta, pydantic, SQLAlchemy
- Web: dash, dash-bootstrap-components, plotly
- Dev: pytest, pytest-cov, flake8, black, mypy

### `.env`

Environment variables (not committed):
```bash
MEXC_API_KEY=your_key
MEXC_API_SECRET=your_secret
SYMBOL=QRL/USDT
BASE_ORDER_USDT=50.0
MAX_POSITION_USDT=500.0
PRICE_OFFSET=0.98
LOG_LEVEL=INFO
```

## Legacy Files (v1.0)

These files are kept for backward compatibility:
- `main.py`: Original entry point
- `config.py`: Old configuration
- `exchange.py`: Old exchange integration
- `strategy.py`: Old strategy logic
- `risk.py`: Old risk checks
- `state.py`: Old state management
- `web/app.py`: Original dashboard

**Recommendation**: Use v2.0 files (`main_new.py`, `src/`, `web/dash_app.py`) for new development.

## Best Practices

### File Naming

- `snake_case` for Python files
- `PascalCase` for class names
- Descriptive module names

### Import Organization

```python
# Standard library
import os
from typing import List

# Third-party
import ccxt
from pydantic import BaseModel

# Local
from src.core.config import AppConfig
from src.strategies.base import BaseStrategy
```

### Type Hints

Always use type hints:
```python
def calculate_price(base: float, offset: float) -> float:
    return base * offset
```

### Documentation

Use docstrings for all public classes and functions:
```python
def analyze(self, ohlcv: List[List[Any]]) -> StrategySignal:
    """
    Analyze market data and generate signal.
    
    Args:
        ohlcv: OHLCV candlestick data
    
    Returns:
        StrategySignal with buy/sell recommendation
    """
```

## Adding New Features

### Adding a New Strategy

1. Create `src/strategies/my_strategy.py`
2. Extend `BaseStrategy`
3. Implement required methods
4. Add tests in `tests/unit/test_my_strategy.py`
5. Update `TradingEngine` to use new strategy

### Adding a New Risk Check

1. Add method to `RiskManager`
2. Return `RiskCheck` object
3. Call in `TradingEngine.execute_trading_cycle()`
4. Add tests in `tests/unit/test_risk.py`

### Adding API Endpoint

1. Add route to `web/dash_app.py`
2. Use existing components (StateManager, ExchangeClient)
3. Return JSONResponse
4. Test manually

## Maintenance

### Database Maintenance

```bash
# Backup database
cp data/state.db data/state.db.backup

# Reset database
rm data/state.db
python main_new.py  # Recreates schema
```

### Log Rotation

Logs stored in `logs/trading.log`. Implement rotation:
```python
# Use Python's RotatingFileHandler
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(
    'logs/trading.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Dependency Updates

```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md): Architecture overview
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md): v1 → v2 migration
- [DEVELOPMENT.md](DEVELOPMENT.md): Development guidelines
- [README.md](../README.md): Project README

## Questions?

See the main documentation or open an issue on GitHub.
