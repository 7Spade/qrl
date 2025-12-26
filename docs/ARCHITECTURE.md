# QRL Trading Bot Architecture (v2.0)

## Overview

This document describes the restructured architecture of the QRL trading bot, implementing a modular, scalable design following industry best practices.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Trading Engine                           │
│              (src/core/engine.py)                           │
│  • Orchestrates all components                             │
│  • Manages trading lifecycle                               │
│  • Handles error recovery                                  │
└─────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Strategies  │ │  Risk Mgmt   │ │  Execution   │ │  Monitoring  │
│              │ │              │ │              │ │              │
│ • Base class │ │ • Position   │ │ • Order mgmt │ │ • Logging    │
│ • EMA strat  │ │   limits     │ │ • Params     │ │ • Alerts     │
│              │ │ • Multi-layer│ │   calc       │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         ↓              ↓              ↓              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│  • Exchange client (API wrapper)                            │
│  • State manager (SQLite)                                   │
│  • Trade history                                            │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
qrl/
├── src/                      # New modular source code
│   ├── core/                 # Core orchestration
│   │   ├── config.py         # Centralized configuration
│   │   └── engine.py         # Trading engine
│   ├── strategies/           # Trading strategies
│   │   ├── base.py           # Strategy interface
│   │   └── ema_strategy.py   # EMA implementation
│   ├── risk/                 # Risk management
│   │   └── manager.py        # Risk checks
│   ├── execution/            # Order execution
│   │   └── order_manager.py  # Order placement
│   ├── data/                 # Data providers
│   │   ├── exchange.py       # Exchange client
│   │   └── state.py          # State management
│   └── monitoring/           # Logging & alerts
│       └── logger.py         # Structured logger
├── web/                      # Web dashboard
│   ├── app_new.py            # Enhanced FastAPI app
│   └── templates/
│       └── dashboard.html    # Improved UI
├── tests/                    # Test suite
│   └── unit/                 # Unit tests
│       ├── test_strategy.py
│       └── test_risk.py
├── main_new.py               # New entry point
└── [legacy files]            # Old implementation
```

## Key Components

### 1. Trading Engine (`src/core/engine.py`)

**Responsibility**: Orchestrate the complete trading cycle

**Key Methods**:
- `execute_trading_cycle()`: Main execution flow
- Coordinates: data fetching → strategy → risk → execution → state update

**Benefits**:
- Single entry point for trading logic
- Centralized error handling
- Clear separation of concerns

### 2. Configuration (`src/core/config.py`)

**Responsibility**: Centralized configuration management

**Features**:
- Pydantic models for validation
- Environment variable loading
- Typed configuration classes:
  - `TradingConfig`: Trading parameters
  - `ExchangeConfig`: API credentials
  - `MonitoringConfig`: Logging settings

**Benefits**:
- Type safety with validation
- Easy to test and mock
- Single source of truth

### 3. Strategy System (`src/strategies/`)

**Responsibility**: Trading signal generation

**Architecture**:
- `BaseStrategy`: Abstract interface
- `EMAAccumulationStrategy`: Concrete implementation
- `StrategySignal`: Typed signal output

**Benefits**:
- Easy to add new strategies
- Testable in isolation
- Clear signal contract

### 4. Risk Management (`src/risk/manager.py`)

**Responsibility**: Multi-layer risk controls

**Features**:
- Position limit checks
- Order size validation
- Daily order count limits
- Utilization calculations

**Benefits**:
- Prevents over-exposure
- Configurable limits
- Detailed metadata for monitoring

### 5. Execution (`src/execution/order_manager.py`)

**Responsibility**: Order placement and tracking

**Features**:
- Order parameter calculation
- Error handling for all failure modes
- Structured result objects

**Benefits**:
- Consistent error handling
- Easy to mock for testing
- Detailed execution metadata

### 6. Data Layer (`src/data/`)

**Components**:
- `ExchangeClient`: CCXT wrapper with error handling
- `StateManager`: SQLite-based persistence
- ORM models for Position and Trade

**Benefits**:
- Abstraction from exchange API
- Automatic schema management
- Trade history tracking

### 7. Monitoring (`src/monitoring/logger.py`)

**Responsibility**: Structured logging and observability

**Features**:
- Consistent log format
- Log levels (INFO, WARNING, ERROR, DEBUG)
- Specialized logging methods:
  - `trade()`: Trade execution logs
  - `strategy_signal()`: Strategy events
  - `risk_check()`: Risk validation logs

**Benefits**:
- Easy to parse logs
- Clear event tracking
- Foundation for alerting

### 8. Web Dashboard (`web/app_new.py`)

**Features**:
- Real-time market data with EMA indicators
- Position utilization visualization
- API endpoints for:
  - `/api/trades`: Trade history
  - `/api/statistics`: Performance stats
  - `/api/logs`: System logs
  - `/api/market`: Market data

**Benefits**:
- No SSH needed for monitoring
- Visual position tracking
- Historical analysis capability

## Design Patterns

### 1. Dependency Injection

Components receive dependencies through constructors:

```python
class TradingEngine:
    def __init__(self, config, strategy):
        self.config = config or AppConfig.load()
        self.strategy = strategy or EMAAccumulationStrategy()
```

**Benefits**: Easy testing, flexible composition

### 2. Strategy Pattern

Trading strategies implement a common interface:

```python
class BaseStrategy(ABC):
    @abstractmethod
    def analyze(self, ohlcv) -> StrategySignal:
        pass
```

**Benefits**: Easy to add strategies, testable

### 3. Result Objects

Operations return structured results instead of raising exceptions:

```python
@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str]
    error: Optional[str]
```

**Benefits**: Explicit error handling, better debugging

### 4. Configuration as Code

Configuration validated with Pydantic:

```python
class TradingConfig(BaseModel):
    max_position_usdt: float = Field(gt=0)
```

**Benefits**: Type safety, validation, IDE support

## Data Flow

### Trading Cycle Flow

```
1. Engine.execute_trading_cycle()
   ↓
2. ExchangeClient.fetch_ohlcv()
   ↓
3. Strategy.analyze() → StrategySignal
   ↓
4. If signal.should_buy:
   ↓
5. StateManager.get_position()
   ↓
6. RiskManager.can_place_order() → RiskCheck
   ↓
7. If risk_check.passed:
   ↓
8. ExchangeClient.fetch_ticker()
   ↓
9. OrderManager.calculate_order_params()
   ↓
10. OrderManager.place_limit_buy() → OrderResult
    ↓
11. StateManager.update_position()
    ↓
12. StateManager.add_trade()
    ↓
13. Logger.trade()
```

## Testing Strategy

### Unit Tests

- **Strategy tests**: Signal generation logic
- **Risk tests**: Limit validation
- **Mocking**: External dependencies (exchange API)

### Test Coverage

Current coverage: 11 unit tests passing
- Risk management: 6 tests
- Strategy: 5 tests

## Migration from v1.0

See `docs/MIGRATION_GUIDE.md` for step-by-step migration instructions.

## Future Enhancements

### Planned Features

1. **Telegram Alerts**
   - Order execution notifications
   - Risk limit warnings
   - Daily summary reports

2. **Advanced Strategies**
   - Multiple strategy support
   - Strategy weighting
   - A/B testing framework

3. **Backtesting**
   - Historical data replay
   - Performance metrics
   - Parameter optimization

4. **Enhanced Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Real-time alerts

5. **Multi-Exchange Support**
   - Abstract exchange interface
   - Multiple exchange clients
   - Cross-exchange arbitrage

## Best Practices

### Adding a New Strategy

1. Extend `BaseStrategy`
2. Implement `analyze()` method
3. Define required candles
4. Return `StrategySignal`
5. Add unit tests

### Adding a New Risk Check

1. Add method to `RiskManager`
2. Return `RiskCheck` object
3. Include metadata for debugging
4. Add unit tests

### Configuration Changes

1. Update appropriate config class
2. Add environment variable
3. Update `.env.example`
4. Document in README

## Performance Considerations

### Optimization Areas

1. **Caching**: EMA calculations cached in memory
2. **Async**: FastAPI endpoints are async
3. **Database**: SQLite with proper indexing
4. **API Calls**: Rate limiting enabled

### Resource Usage

- **Memory**: ~50MB baseline
- **CPU**: Minimal (event-driven)
- **Disk**: SQLite database grows with trade history

## Security

### Best Practices Implemented

1. **API Keys**: Environment variables only
2. **Validation**: Pydantic input validation
3. **Logging**: No sensitive data in logs
4. **Error Handling**: No stack traces exposed

## Monitoring & Observability

### Log Levels

- **DEBUG**: Detailed execution flow
- **INFO**: Normal operations
- **WARNING**: Risk checks failed
- **ERROR**: Execution failures

### Key Metrics to Monitor

1. Trade execution success rate
2. Position utilization %
3. API response times
4. Daily order count
5. Risk check pass/fail ratio

## Conclusion

The restructured architecture provides:
- ✅ Clear separation of concerns
- ✅ Testable components
- ✅ Easy to extend
- ✅ Production-ready monitoring
- ✅ Type safety and validation

For questions or contributions, see `CONTRIBUTING.md`.
