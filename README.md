# QRL Trading Bot

A cryptocurrency trading bot for QRL/USDT pair on MEXC exchange, implementing a low-risk accumulation strategy based on EMA (Exponential Moving Average) indicators.

## 🎯 Features

- **Smart Entry Strategy**: Uses EMA20/EMA60 crossover for low-risk entry points
- **Risk Management**: Configurable position limits and order sizes
- **Automated Trading**: Autonomous limit order placement
- **Position Tracking**: SQLite-based position state persistence
- **Web Dashboard**: Real-time monitoring via FastAPI interface
- **Exchange Integration**: MEXC exchange via CCXT library

## 📋 Prerequisites

- Python 3.9 or higher
- MEXC exchange account with API keys
- Basic understanding of cryptocurrency trading risks

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/7Spade/qrl.git
cd qrl

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
MEXC_API_KEY=your_api_key_here
MEXC_API_SECRET=your_api_secret_here
SYMBOL=QRL/USDT
```

### 3. Run the Bot

**Execute a trading cycle**:
```bash
python main.py
```

**Start the web dashboard**:
```bash
cd web
uvicorn app:app --reload
```

Then open http://localhost:8000 in your browser.

## 📊 Trading Strategy

### Buy Conditions

The bot places a limit buy order when **both** conditions are met:

1. **Price near support**: Current price ≤ EMA60 × 1.02 (within 2% of 60-day average)
2. **Positive momentum**: EMA20 ≥ EMA60 (short-term trend is upward)

### Risk Management

- **Single order size**: 50 USDT (configurable via `BASE_ORDER_USDT`)
- **Maximum position**: 500 USDT (configurable via `MAX_POSITION_USDT`)
- **Limit order offset**: 2% below current price (configurable via `PRICE_OFFSET`)

### Technical Details

- **Data timeframe**: 1 day (daily candles)
- **Historical data**: 120 days for indicator calculation
- **Indicators**: EMA20, EMA60 calculated using `ta` library

## 🔧 Configuration Options

Edit `config.py` to customize:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SYMBOL` | `QRL/USDT` | Trading pair |
| `TIMEFRAME` | `1d` | Candle timeframe |
| `BASE_ORDER_USDT` | `50` | Size per order in USDT |
| `MAX_POSITION_USDT` | `500` | Maximum total position |
| `PRICE_OFFSET` | `0.98` | Limit price multiplier (0.98 = 2% discount) |

## 📁 Project Structure

```
qrl/
├── config.py           # Configuration parameters
├── exchange.py         # MEXC exchange wrapper
├── main.py            # Main execution script
├── risk.py            # Position limit checks
├── state.py           # SQLite state management
├── strategy.py        # EMA-based buy signal
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
├── data/              # SQLite database (auto-created)
└── web/
    ├── app.py         # FastAPI dashboard
    └── templates/
        └── index.html # Dashboard UI
```

## 🔍 Component Details

### Main Script (`main.py`)
Orchestrates the trading logic:
1. Fetch historical OHLCV data
2. Evaluate strategy conditions
3. Check risk limits
4. Place limit buy order if conditions met
5. Update position state

### Strategy (`strategy.py`)
Implements EMA-based technical analysis:
- Calculates EMA20 and EMA60 from price history
- Returns `True` when buy conditions are satisfied

### Risk Management (`risk.py`)
Simple position limit validation:
- Prevents orders when maximum position is reached

### State Management (`state.py`)
Persists current position value:
- Uses SQLite database for reliability
- Auto-creates `data/` directory on first run

### Web Dashboard (`web/app.py`)
Provides real-time monitoring:
- Current QRL/USDT price
- Total position in USDT
- Last update timestamp

## 🛡️ Security Best Practices

1. **Never commit `.env`**: Keep API keys private
2. **Use read-only keys**: For dashboard monitoring
3. **Test on testnet**: Before live trading
4. **Monitor regularly**: Check bot status frequently
5. **Set reasonable limits**: Don't over-leverage

## ⚠️ Risk Disclosure

**IMPORTANT**: Cryptocurrency trading involves substantial risk of loss.

- This bot is provided for educational purposes
- No guarantees of profit or performance
- You are responsible for your own trading decisions
- Always trade with funds you can afford to lose
- Backtest thoroughly before live deployment

## 🔄 Scheduling

To run the bot automatically, use cron (Linux/Mac) or Task Scheduler (Windows):

**Cron example** (runs daily at 9 AM):
```bash
0 9 * * * cd /path/to/qrl && /usr/bin/python3 main.py >> logs/bot.log 2>&1
```

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Database errors
```bash
rm -rf data/  # Reset database
python main.py  # Recreate on next run
```

### API authentication failures
- Verify `.env` credentials are correct
- Check API key permissions on MEXC
- Ensure rate limits aren't exceeded

## 📈 Future Enhancements

- [ ] Implement sell/exit strategy
- [ ] Add comprehensive logging
- [ ] Create unit test suite
- [ ] Add backtesting framework
- [ ] Implement notification system
- [ ] Support multiple trading pairs
- [ ] Add performance analytics
- [ ] Docker containerization

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review MEXC API documentation

## 🙏 Acknowledgments

- [CCXT](https://github.com/ccxt/ccxt) - Cryptocurrency exchange integration
- [TA-Lib](https://github.com/bukosabino/ta) - Technical analysis indicators
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

---

**Disclaimer**: This software is for educational purposes only. Use at your own risk.
