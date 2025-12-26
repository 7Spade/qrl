# Quick Start Guide - v2.0

## 🚀 Getting Started in 5 Minutes

### Prerequisites

```bash
# Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Option 1: Quick Test (No Configuration Needed)

```bash
# Test module imports
python -c "from src.core.engine import TradingEngine; print('✅ Modules OK')"

# Run unit tests
pytest tests/ -v
# Expected: 11 passed in 0.74s
```

### Option 2: Run Trading Bot

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your MEXC API credentials
nano .env  # or your preferred editor

# 3. Run the new trading engine
python main_new.py
```

### Option 3: Start Web Dashboard

```bash
# Start the enhanced dashboard
uvicorn web.app_new:app --reload --port 8000

# Open browser to http://localhost:8000
```

---

## 📖 Documentation Map

**New to the project?** Start here:

1. **5-Minute Overview**
   - `docs/VISUAL_COMPARISON.md` - See what changed

2. **Understanding the Architecture** (15 minutes)
   - `docs/RESTRUCTURING_SUMMARY.md` - Complete summary
   - `docs/ARCHITECTURE.md` - Design patterns

3. **Migrating from v1.0** (30 minutes)
   - `docs/MIGRATION_GUIDE.md` - Step-by-step instructions

4. **Deep Dive** (1 hour)
   - `docs/PROJECT_STRUCTURE.md` - Module reference
   - Source code in `src/`

---

## 🎯 Common Tasks

### Run the Trading Bot

```bash
# New version (recommended)
python main_new.py

# Old version (still works)
python main.py
```

### Start the Dashboard

```bash
# New enhanced dashboard
uvicorn web.app_new:app --reload --port 8000

# Old basic dashboard
uvicorn web.app:app --reload --port 8001
```

### Run Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/unit/test_strategy.py -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### View Logs

```bash
# Real-time logs
tail -f logs/trading.log

# Last 50 lines
tail -n 50 logs/trading.log

# Search logs
grep "BUY" logs/trading.log
```

### Check Trade History

```bash
# Using Python
python -c "
from src.data.state import StateManager
state = StateManager()
trades = state.get_trade_history(limit=10)
for t in trades:
    print(f'{t[\"timestamp\"]}: {t[\"action\"]} @ {t[\"price\"]:.6f}')
"

# Using SQLite
sqlite3 data/state.db "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

```bash
# Required
MEXC_API_KEY=your_api_key_here
MEXC_API_SECRET=your_api_secret_here

# Trading parameters (optional, defaults shown)
SYMBOL=QRL/USDT
BASE_ORDER_USDT=50.0
MAX_POSITION_USDT=500.0
PRICE_OFFSET=0.98

# Monitoring (optional)
LOG_LEVEL=INFO
LOG_FILE=logs/trading.log

# Telegram (future feature, optional)
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Code Configuration

```python
# Load configuration
from src.core.config import AppConfig

config = AppConfig.load()
print(config.trading.symbol)  # "QRL/USDT"
print(config.trading.max_position_usdt)  # 500.0

# Override configuration
config.trading.base_order_usdt = 100.0
```

---

## 🧪 Testing Your Setup

### 1. Test Imports

```python
python -c "
from src.core.engine import TradingEngine
from src.strategies.ema_strategy import EMAAccumulationStrategy
from src.risk.manager import RiskManager
print('✅ All modules imported successfully')
"
```

### 2. Test Database

```python
python -c "
from src.data.state import StateManager
state = StateManager()
position = state.get_position()
print(f'✅ Database working. Position: {position} USDT')
"
```

### 3. Test Exchange Connection (requires API keys)

```python
python -c "
from src.core.config import AppConfig
from src.data.exchange import ExchangeClient

config = AppConfig.load()
client = ExchangeClient(config.exchange)
ticker = client.fetch_ticker('QRL/USDT')
print(f'✅ Exchange connected. QRL price: \${ticker[\"last\"]:.6f}')
"
```

### 4. Test Strategy

```python
python -c "
from src.strategies.ema_strategy import EMAAccumulationStrategy

strategy = EMAAccumulationStrategy()
print(f'✅ Strategy initialized: {strategy.name}')
print(f'   Required candles: {strategy.get_required_candles()}')
"
```

### 5. Run Complete Test Suite

```bash
pytest tests/ -v
# Should see: 11 passed
```

---

## 🆘 Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Run from project root
```bash
cd /path/to/qrl
python main_new.py
```

### Database Errors

**Error**: `no such table: positions`

**Solution**: Delete and recreate database
```bash
rm data/state.db
python main_new.py  # Recreates schema
```

### Configuration Errors

**Error**: `validation error for TradingConfig`

**Solution**: Check your values in `.env`
```bash
# Ensure all numeric values are valid
BASE_ORDER_USDT=50.0      # Must be > 0
MAX_POSITION_USDT=500.0   # Must be >= BASE_ORDER_USDT
PRICE_OFFSET=0.98         # Must be 0 < x < 1
```

### API Connection Errors

**Error**: `ccxt.AuthenticationError`

**Solution**: Verify API credentials
```bash
# Check .env file has correct keys
cat .env | grep MEXC_API

# Test API connection
python -c "from exchange import get_exchange; get_exchange()"
```

---

## 📊 Dashboard Features

### Access the Dashboard

```bash
uvicorn web.app_new:app --reload --port 8000
# Visit http://localhost:8000
```

### Available Endpoints

- `GET /` - Main dashboard
- `GET /health` - Health check
- `GET /api/trades` - Trade history (JSON)
- `GET /api/statistics` - Performance stats (JSON)
- `GET /api/logs` - System logs (JSON)
- `GET /api/market` - Market data with indicators (JSON)

### Example API Usage

```bash
# Get trade history
curl http://localhost:8000/api/trades?limit=5

# Get statistics
curl http://localhost:8000/api/statistics

# Get market data
curl http://localhost:8000/api/market
```

---

## 🔄 Deployment

### Local Deployment

```bash
# Run in background with nohup
nohup python main_new.py > output.log 2>&1 &

# Or use screen
screen -S qrl-bot
python main_new.py
# Press Ctrl+A, D to detach
```

### Cron Job

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 9 AM)
0 9 * * * cd /path/to/qrl && python main_new.py >> logs/cron.log 2>&1
```

### Docker (if using Cloud Run)

```dockerfile
# Update Dockerfile entry point
CMD ["python", "main_new.py"]
```

### Cloud Run

```bash
# Deploy with new entry point
gcloud builds submit --config cloudbuild.yaml
```

---

## 🎯 Next Steps

### Learning Path

1. ✅ **Complete this quick start**
2. 📖 Read `docs/VISUAL_COMPARISON.md` (5 min)
3. 📖 Read `docs/RESTRUCTURING_SUMMARY.md` (15 min)
4. 🧪 Run all tests: `pytest tests/ -v`
5. 🌐 Start dashboard and explore
6. 📖 Deep dive into `docs/ARCHITECTURE.md`

### Extending the Bot

Want to add features? See:
- **New Strategy**: `docs/PROJECT_STRUCTURE.md` → "Adding a New Strategy"
- **New Risk Check**: `docs/PROJECT_STRUCTURE.md` → "Adding a New Risk Check"
- **New API Endpoint**: `docs/PROJECT_STRUCTURE.md` → "Adding API Endpoint"

---

## 📚 Documentation Index

| Document | Purpose | Time |
|----------|---------|------|
| `QUICK_START_V2.md` | This guide | 5 min |
| `VISUAL_COMPARISON.md` | Before/after comparison | 5 min |
| `RESTRUCTURING_SUMMARY.md` | Complete overview | 15 min |
| `ARCHITECTURE.md` | Design deep dive | 30 min |
| `MIGRATION_GUIDE.md` | v1→v2 upgrade | 30 min |
| `PROJECT_STRUCTURE.md` | Module reference | 1 hour |

---

## 🤝 Getting Help

### Documentation
- Check relevant doc file above
- Search logs: `grep "ERROR" logs/trading.log`

### Issues
- Open GitHub issue with:
  - Error message
  - Steps to reproduce
  - Environment details

### Questions
- Review existing documentation first
- Check test files for usage examples

---

## ✅ Checklist

Before running in production:

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file configured with valid API keys
- [ ] Database initialized: `python main_new.py` (runs once)
- [ ] Tests passing: `pytest tests/`
- [ ] Dashboard accessible: `uvicorn web.app_new:app --reload`
- [ ] Logs directory created: `mkdir -p logs`
- [ ] Documentation reviewed
- [ ] Backup plan in place (see `MIGRATION_GUIDE.md`)

---

**Version**: 2.0.0
**Status**: Production Ready ✅
**Support**: See documentation files above
