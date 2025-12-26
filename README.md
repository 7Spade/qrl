# QRL Trading Bot

A cryptocurrency trading bot for QRL/USDT pair on MEXC exchange, implementing a low-risk accumulation strategy based on EMA (Exponential Moving Average) indicators.

## 🎯 Features

- **Smart Entry Strategy**: EMA20/EMA60 crossover for low-risk entry
- **Risk Management**: Configurable position limits and order sizes
- **Automated Trading**: Autonomous limit order placement
- **Position Tracking**: SQLite-based state persistence
- **Web Dashboard**: Real-time monitoring via FastAPI
- **Cloud Ready**: Docker support for Google Cloud Run
- **Redis Caching**: Optional high-performance caching with advanced features (see [Redis Best Practices](#-redis-caching-best-practices))

## 📋 Prerequisites

- Python 3.9 or higher
- MEXC exchange account with API keys
  - Create at: https://www.mexc.com/user/openapi
  - Enable "Spot Trading" permission
- (Optional) Google Cloud account for deployment

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone and install
git clone https://github.com/7Spade/qrl.git
cd qrl
pip install -r requirements.txt

# 2. Configure (see docs/MEXC_API_SETUP.md for details)
cp .env.example .env
# Edit .env with your MEXC API credentials

# 3. Run
python main.py              # Trading bot
uvicorn web.app:app --reload  # Web dashboard
```

### Cloud Deployment

```bash
gcloud builds submit --config cloudbuild.yaml
```

See [docs/AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md) for authentication setup.

## 📊 Trading Strategy

**Buy Conditions** (both required):
1. Price near support: Current price ≤ EMA60 × 1.02
2. Positive momentum: EMA20 ≥ EMA60

**Risk Management**:
- Order size: 50 USDT (configurable)
- Max position: 500 USDT (configurable)
- Limit offset: 2% below market price

## 🔧 Configuration

Edit `config.py` to customize:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SYMBOL` | `QRL/USDT` | Trading pair |
| `BASE_ORDER_USDT` | `50` | Order size in USDT |
| `MAX_POSITION_USDT` | `500` | Maximum position size |
| `PRICE_OFFSET` | `0.98` | Limit price discount (2%) |

## 📁 Project Structure

```
qrl/
├── config.py           # Configuration and settings
├── exchange.py         # MEXC exchange integration
├── main.py            # Main trading logic
├── risk.py            # Risk management
├── state.py           # Position tracking (SQLite)
├── strategy.py        # EMA-based strategy
├── web/app.py         # FastAPI dashboard
├── Dockerfile         # Container configuration
├── cloudbuild.yaml    # Cloud Build setup
├── pyproject.toml     # Python project config
└── docs/              # Documentation
    ├── QUICK_REFERENCE.md
    ├── MEXC_API_SETUP.md
    ├── AUTHENTICATION_GUIDE.md
    ├── DEVELOPMENT.md
    └── 快速開始.md
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Quick Reference](docs/QUICK_REFERENCE.md) | Common tasks and commands |
| [MEXC API Setup](docs/MEXC_API_SETUP.md) | API credentials guide |
| [Authentication Guide](docs/AUTHENTICATION_GUIDE.md) | Cloud Run authentication |
| [Development Guide](docs/DEVELOPMENT.md) | Code standards and setup |
| [快速開始](docs/快速開始.md) | Chinese quick start guide |
| [CHANGELOG](CHANGELOG.md) | Version history |

## 🛡️ Security Best Practices

- ✅ Never commit `.env` file to version control
- ✅ Use read-only API keys for monitoring
- ✅ Test thoroughly before live trading
- ✅ Set reasonable position limits
- ✅ Monitor bot activity regularly

## ⚠️ Risk Disclosure

**IMPORTANT**: Cryptocurrency trading involves substantial risk of loss. This bot is provided for educational purposes only. No warranties or guarantees of profit. Always trade responsibly with funds you can afford to lose.

## 🔄 Automation Examples

**Cron (Linux/Mac)**:
```bash
0 9 * * * cd /path/to/qrl && python3 main.py >> logs/bot.log 2>&1
```

**Cloud Scheduler**:
```bash
gcloud scheduler jobs create http qrl-trader \
  --schedule="0 9 * * *" \
  --uri="YOUR_CLOUD_RUN_URL" \
  --http-method=GET
```

## 🐛 Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Module not found | `pip install -r requirements.txt` |
| Database errors | `rm -rf data/ && python main.py` |
| API authentication | Check `.env` credentials |
| 403 Cloud Run error | See [Authentication Guide](docs/AUTHENTICATION_GUIDE.md) |

For detailed troubleshooting, see [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md).

## 📦 Redis Caching Best Practices

The QRL trading bot includes optional Redis caching for improved performance. Redis caching is production-ready with advanced features:

### Features

- **Namespace Isolation**: Separate cache keys per environment (dev/staging/prod)
- **Version Control**: Built-in cache versioning for schema migrations
- **Configurable TTLs**: Fine-tuned cache expiration per data type
- **Safe Invalidation**: Granular cache clearing without affecting shared Redis
- **Error Handling**: Robust JSON serialization for trading data types (Decimal, datetime)
- **Memory Management**: LRU eviction policy prevents unbounded growth
- **Cache Warming**: Optional preloading of frequently accessed data

### Configuration

Add to your `.env` file:

```bash
# Redis connection
REDIS_URL=redis://default:password@your-redis-host:6379

# Optional: TTL configuration (in seconds)
REDIS_CACHE_TTL=60              # Default TTL
REDIS_CACHE_TTL_TICKER=5        # Fast-changing ticker data
REDIS_CACHE_TTL_OHLCV=60        # Relatively stable OHLCV data
REDIS_CACHE_TTL_DEALS=10        # Moderately changing deals
REDIS_CACHE_TTL_ORDERBOOK=5     # Fast-changing order book

# Optional: Namespace for environment separation
REDIS_NAMESPACE=qrl             # Use "qrl-dev", "qrl-staging", etc.
```

### Usage Examples

```python
from src.data.exchange import ExchangeClient

# Automatic caching (uses configured TTLs)
data = exchange_client.fetch_ohlcv("QRL/USDT", "1d", 120)

# Force bypass cache
data = exchange_client.fetch_ticker("QRL/USDT", use_cache=False)

# Cache invalidation
exchange_client.invalidate_cache(symbol="QRL/USDT")  # Clear specific symbol
exchange_client.invalidate_cache()                   # Clear all cache

# Cache statistics
stats = exchange_client.get_cache_stats()
```

### Benefits

- **Performance**: 10-100x faster for repeated data fetches
- **Cost Reduction**: Fewer API calls to MEXC exchange
- **Rate Limit Protection**: Reduces risk of hitting API rate limits
- **Resilience**: Continues serving cached data during brief network issues

For detailed Redis implementation details, see [docs/REDIS_IMPROVEMENTS.md](docs/REDIS_IMPROVEMENTS.md).

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow code standards in [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
4. Submit a pull request

---

**Disclaimer**: This software is for educational purposes only. Use at your own risk.
