# QRL Trading Bot

A cryptocurrency trading bot for QRL/USDT pair on MEXC exchange, implementing a low-risk accumulation strategy based on EMA (Exponential Moving Average) indicators.

## 🎯 Features

- **Smart Entry Strategy**: Uses EMA20/EMA60 crossover for low-risk entry points
- **Risk Management**: Configurable position limits and order sizes
- **Automated Trading**: Autonomous limit order placement
- **Position Tracking**: SQLite-based position state persistence
- **Web Dashboard**: Real-time monitoring via FastAPI interface
- **Cloud Ready**: Docker support for Google Cloud Run deployment

## 📋 Prerequisites

- Python 3.9 or higher
- MEXC exchange account with API keys
- Basic understanding of cryptocurrency trading risks

## 🚀 Quick Start

### Local Development

#### 1. Installation

```bash
git clone https://github.com/7Spade/qrl.git
cd qrl
pip install -r requirements.txt
```

#### 2. Configuration

```bash
cp .env.example .env
# Edit .env with your MEXC API credentials
```

#### 3. Run

```bash
# Run trading bot
python main.py

# Run web dashboard
uvicorn web.app:app --reload
```

### Google Cloud Run Deployment

```bash
# Deploy with Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

The deployment process automatically configures public access. The IAM policy binding is included in the Cloud Build configuration, so you don't need to manually run the `add-iam-policy-binding` command.

**Note**: After deployment, it may take 30-60 seconds for the service to be fully accessible. If you encounter a 403 error immediately after deployment, wait a moment and try again.

## 📊 Trading Strategy

### Buy Conditions

The bot places a limit buy order when **both** conditions are met:

1. **Price near support**: Current price ≤ EMA60 × 1.02
2. **Positive momentum**: EMA20 ≥ EMA60

### Risk Management

- **Single order**: 50 USDT (configurable)
- **Max position**: 500 USDT (configurable)
- **Limit offset**: 2% below market price

## 🔧 Configuration

Edit `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SYMBOL` | `QRL/USDT` | Trading pair |
| `BASE_ORDER_USDT` | `50` | Order size |
| `MAX_POSITION_USDT` | `500` | Max position |
| `PRICE_OFFSET` | `0.98` | Limit price (2% discount) |

## 📁 Project Structure

```
qrl/
├── config.py          # Configuration
├── exchange.py        # MEXC integration
├── main.py           # Trading logic
├── risk.py           # Risk checks
├── state.py          # Position tracking
├── strategy.py       # EMA strategy
├── web/app.py        # Dashboard
├── Dockerfile        # Container image
└── cloudbuild.yaml   # Cloud Build config
```

## 🛡️ Security

- Never commit `.env` file
- Use read-only API keys for dashboard
- Test thoroughly before live trading
- Set reasonable position limits

## ⚠️ Risk Disclosure

**IMPORTANT**: Cryptocurrency trading involves substantial risk of loss. This bot is for educational purposes only. No guarantees of profit. Always trade responsibly with funds you can afford to lose.

## 🔄 Automation

**Cron (Linux/Mac)**:
```bash
0 9 * * * cd /path/to/qrl && python3 main.py >> logs/bot.log 2>&1
```

**Cloud Scheduler** (for Cloud Run):
```bash
gcloud scheduler jobs create http qrl-trader \
  --schedule="0 9 * * *" \
  --uri="YOUR_CLOUD_RUN_URL/trade" \
  --http-method=POST
```

## 🐛 Troubleshooting

### Local Issues

**Module errors**: `pip install -r requirements.txt`

**Database errors**: `rm -rf data/ && python main.py`

**API errors**: Verify credentials in `.env`

### Cloud Run Issues

**403 Forbidden Error**:

The updated deployment configuration automatically sets public access. If you still encounter this error:

1. **Wait 30-60 seconds** - The service may be initializing
2. **Verify IAM policy manually** (if needed):
```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```
3. **Check service status**:
```bash
gcloud run services describe qrl-bot --region=asia-east1
```

**Why this happens**: Google Cloud Run requires explicit IAM policy to allow unauthenticated access. The updated `cloudbuild.yaml` now includes this step automatically.

**Port/Connection Issues**:
- Cloud Run uses PORT environment variable (configured in Dockerfile)
- Ensure `--port 8080` is set in cloudbuild.yaml

**Deployment Fails**:
```bash
# Check logs
gcloud run services logs read qrl-bot --region=asia-east1

# Redeploy
gcloud builds submit --config cloudbuild.yaml
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Fork, create feature branch, submit PR.

---

**Disclaimer**: Educational purposes only. Use at your own risk.
