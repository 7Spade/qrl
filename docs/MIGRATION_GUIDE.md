# Migration Guide: v1.0 → v2.0

This guide helps you migrate from the flat structure (v1.0) to the modular architecture (v2.0).

## Overview

**v1.0 Structure** (Flat):
```
qrl/
├── config.py
├── exchange.py
├── strategy.py
├── risk.py
├── state.py
└── main.py
```

**v2.0 Structure** (Modular):
```
qrl/
├── src/
│   ├── core/
│   ├── strategies/
│   ├── risk/
│   ├── execution/
│   ├── data/
│   └── monitoring/
├── main_new.py
└── [legacy files]
```

## Migration Steps

### Step 1: Backup Current Setup

```bash
# Backup your .env file
cp .env .env.backup

# Backup your database
cp data/state.db data/state.db.backup
```

### Step 2: Update Dependencies

No changes needed! The `requirements.txt` remains the same.

```bash
pip install -r requirements.txt
```

### Step 3: Test New Implementation

#### Option A: Side-by-Side Testing

Run the new version alongside the old:

```bash
# Old version (still works)
python main.py

# New version (test first)
python main_new.py
```

#### Option B: Verify Modules Load

```bash
python3 -c "
from src.core.engine import TradingEngine
engine = TradingEngine()
print('✅ New modules loaded successfully')
"
```

### Step 4: Update Deployment

#### For Local Deployments

Replace `main.py` with `main_new.py`:

```bash
# Backup old main
mv main.py main_old.py

# Use new main
cp main_new.py main.py
```

#### For Cloud Run

Update `Dockerfile` to use new entry point:

```dockerfile
# Change from:
CMD ["python", "main.py"]

# To:
CMD ["python", "main_new.py"]
```

Or update `cloudbuild.yaml` if needed.

#### For Cron Jobs

Update your cron command:

```bash
# Old
0 9 * * * python /path/to/qrl/main.py

# New
0 9 * * * python /path/to/qrl/main_new.py
```

### Step 5: Update Web Dashboard

#### Option A: Run New Dashboard Separately

```bash
# Old dashboard (port 8000)
uvicorn web.app:app --port 8000

# New dashboard (port 8001)
uvicorn web.app_new:app --port 8001
```

#### Option B: Replace Old Dashboard

```bash
# Backup
mv web/app.py web/app_old.py

# Replace
cp web/app_new.py web/app.py
```

### Step 6: Environment Variables

No changes required! The new version uses the same `.env` variables:

```bash
MEXC_API_KEY=your_key
MEXC_API_SECRET=your_secret
SYMBOL=QRL/USDT
BASE_ORDER_USDT=50.0
MAX_POSITION_USDT=500.0
PRICE_OFFSET=0.98
```

**Optional new variables** for enhanced monitoring:

```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log

# Telegram (future feature)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Code Comparison

### Old vs New: Main Entry Point

#### v1.0 (main.py)

```python
from exchange import get_exchange
from strategy import should_buy
from risk import can_buy
from state import get_position_usdt

exchange = get_exchange()
ohlcv = exchange.fetch_ohlcv("QRL/USDT", "1d", 120)

if should_buy(ohlcv):
    position = get_position_usdt()
    if can_buy(position, 500):
        # Place order...
```

#### v2.0 (main_new.py)

```python
from src.core.engine import TradingEngine

engine = TradingEngine()
engine.execute_trading_cycle()
```

**Benefits**:
- Single entry point
- Automatic orchestration
- Better error handling

### Old vs New: Strategy

#### v1.0 (strategy.py)

```python
def should_buy(ohlcv: List) -> bool:
    # Calculate EMA
    # Return boolean
    return near_support and positive_momentum
```

#### v2.0 (src/strategies/ema_strategy.py)

```python
class EMAAccumulationStrategy(BaseStrategy):
    def analyze(self, ohlcv) -> StrategySignal:
        # Calculate EMA
        return StrategySignal(
            should_buy=should_buy,
            metadata={...}
        )
```

**Benefits**:
- Reusable base class
- Rich metadata
- Easy to extend

### Old vs New: Risk Management

#### v1.0 (risk.py)

```python
def can_buy(position: float, max_position: float) -> bool:
    return position < max_position
```

#### v2.0 (src/risk/manager.py)

```python
class RiskManager:
    def can_place_order(self, position, order_size) -> RiskCheck:
        # Multiple checks
        return RiskCheck(
            passed=True/False,
            reason="...",
            metadata={...}
        )
```

**Benefits**:
- Multi-layer checks
- Detailed reasons
- Metadata for debugging

## Database Migration

### Schema Changes

The new version adds a `trades` table for history tracking:

```sql
-- Automatically created by StateManager
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    action TEXT,
    symbol TEXT,
    price REAL,
    amount REAL,
    cost REAL,
    strategy TEXT
);
```

**Migration is automatic**: The database schema updates on first run.

**Your existing position data is preserved** in the `positions` table (formerly `state`).

### Manual Migration (if needed)

If you want to preserve old data structure:

```python
from src.data.state import StateManager
from state import get_position_usdt

# Get old position
old_position = get_position_usdt()

# Create new manager and set position
manager = StateManager()
manager.update_position(old_position)
```

## API Changes

### Configuration

#### v1.0

```python
from config import SYMBOL, BASE_ORDER_USDT

print(SYMBOL)  # "QRL/USDT"
```

#### v2.0

```python
from src.core.config import AppConfig

config = AppConfig.load()
print(config.trading.symbol)  # "QRL/USDT"
```

### Exchange Client

#### v1.0

```python
from exchange import get_exchange

exchange = get_exchange()
ticker = exchange.fetch_ticker("QRL/USDT")
```

#### v2.0

```python
from src.data.exchange import ExchangeClient
from src.core.config import AppConfig

config = AppConfig.load()
client = ExchangeClient(config.exchange)
ticker = client.fetch_ticker("QRL/USDT")
```

### State Management

#### v1.0

```python
from state import get_position_usdt, update_position_usdt

position = get_position_usdt()
update_position_usdt(100.0)
```

#### v2.0

```python
from src.data.state import StateManager

manager = StateManager()
position = manager.get_position()
manager.update_position(100.0)

# New: Trade history
manager.add_trade("BUY", "QRL/USDT", 0.45, 111, 50)
trades = manager.get_trade_history(limit=10)
```

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Expected Output

```
tests/unit/test_risk.py ......        [54%]
tests/unit/test_strategy.py .....     [100%]

11 passed in 0.74s
```

## Rollback Plan

If you need to rollback to v1.0:

```bash
# Restore old files
mv main_old.py main.py
mv web/app_old.py web/app.py

# Restore database (if needed)
cp data/state.db.backup data/state.db

# Restore environment
cp .env.backup .env
```

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Ensure you're running from the project root:

```bash
cd /path/to/qrl
python main_new.py
```

### Database Errors

**Error**: `SQLAlchemy error`

**Solution**: Delete and recreate database:

```bash
rm data/state.db
python main_new.py  # Creates new schema
```

### Configuration Errors

**Error**: `Pydantic validation error`

**Solution**: Check your `.env` values:

```bash
# Ensure numeric values are valid
BASE_ORDER_USDT=50.0    # Must be > 0
MAX_POSITION_USDT=500.0  # Must be >= BASE_ORDER_USDT
PRICE_OFFSET=0.98        # Must be 0 < x < 1
```

## Benefits Summary

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **Code Organization** | Flat files | Modular packages |
| **Testing** | Manual | Unit tests (11 tests) |
| **Configuration** | Module-level vars | Validated Pydantic models |
| **Error Handling** | Basic | Structured with metadata |
| **Logging** | Print statements | Structured logging |
| **Trade History** | None | Full SQLite tracking |
| **Extensibility** | Difficult | Easy (base classes) |
| **Type Safety** | Basic | Full type hints |
| **Web Dashboard** | Basic | Enhanced with charts |

## Next Steps

After migrating:

1. ✅ Verify trading functionality works
2. ✅ Check web dashboard displays correctly
3. ✅ Review logs for any issues
4. ✅ Test one trading cycle manually
5. ✅ Enable production deployment

## Getting Help

- **Documentation**: See `docs/ARCHITECTURE.md`
- **Issues**: Open a GitHub issue
- **Questions**: Check existing documentation

## Version Compatibility

- **Python**: 3.9+ (same as v1.0)
- **Dependencies**: Same as v1.0
- **Database**: Backward compatible
- **API**: MEXC API unchanged

The migration is designed to be **non-breaking** and **reversible**.
