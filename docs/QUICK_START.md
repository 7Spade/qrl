# Quick Start Guide

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

# 3. Run the trading engine
python main.py
```

### Option 3: Start Web Dashboard

```bash
# Start the dashboard
uvicorn web.app:app --reload --port 8000

# Open browser to http://localhost:8000
```

---

## 📖 Documentation

**Architecture Overview**:
- `docs/ARCHITECTURE.md` - Complete architecture guide
- `docs/PROJECT_STRUCTURE.md` - Module reference
- `docs/RESTRUCTURING_SUMMARY.md` - Project summary

---

## 🎯 Common Tasks

### Run the Trading Bot

```bash
python main.py
```

### Start the Dashboard

```bash
uvicorn web.app:app --reload --port 8000
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
```

---

## 🧪 Testing Your Setup

### 1. Test Imports

```bash
python -c "from src.core.engine import TradingEngine; print('✅ OK')"
```

### 2. Test Database

```bash
python -c "from src.data.state import StateManager; print('✅ OK')"
```

### 3. Run Tests

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
python main.py
```

### Database Errors

**Error**: `no such table: positions`

**Solution**: Delete and recreate database
```bash
rm data/state.db
python main.py  # Recreates schema
```

---

## 📊 Dashboard Features

### Access the Dashboard

```bash
uvicorn web.app:app --reload --port 8000
# Visit http://localhost:8000
```

### Available Endpoints

- `GET /` - Main dashboard
- `GET /health` - Health check
- `GET /api/trades` - Trade history (JSON)
- `GET /api/statistics` - Performance stats (JSON)
- `GET /api/logs` - System logs (JSON)
- `GET /api/market` - Market data with indicators (JSON)

---

## 🔄 Deployment

### Local Deployment

```bash
# Run in background with nohup
nohup python main.py > output.log 2>&1 &
```

### Cron Job

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 9 AM)
0 9 * * * cd /path/to/qrl && python main.py >> logs/cron.log 2>&1
```

### Docker (Cloud Run)

```bash
# Deploy
gcloud builds submit --config cloudbuild.yaml
```

---

## ✅ Checklist

Before running in production:

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file configured with valid API keys
- [ ] Database initialized: `python main.py` (runs once)
- [ ] Tests passing: `pytest tests/`
- [ ] Dashboard accessible: `uvicorn web.app:app --reload`
- [ ] Logs directory created: `mkdir -p logs`

---

**Status**: Production Ready ✅
**Version**: 2.0.0
