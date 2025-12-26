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
  - Create API keys at: https://www.mexc.com/user/openapi
  - MEXC provides two credentials:
    - **Access Key** (use as MEXC_API_KEY in .env)
    - **Secret Key** (use as MEXC_API_SECRET in .env)
  - Enable "Spot Trading" permission
  - For subaccount trading, specify the subaccount name in `.env`
- Basic understanding of cryptocurrency trading risks
- (Optional) Google Cloud account for Cloud Run deployment

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
# Get your API keys from: https://www.mexc.com/user/openapi
#
# MEXC API Credentials:
#   - MEXC_API_KEY: Your MEXC Access Key
#   - MEXC_API_SECRET: Your MEXC Secret Key
#   - MEXC_SUBACCOUNT: (Optional) Subaccount name for subaccount trading
```

**Important**: MEXC provides an "Access Key" and "Secret Key" when you create API credentials. 
- Use the **Access Key** as `MEXC_API_KEY`
- Use the **Secret Key** as `MEXC_API_SECRET`

#### 3. Run

```bash
# Run trading bot
python main.py

# Run web dashboard
uvicorn web.app:app --reload
```

### Google Cloud Run Deployment

```bash
# Deploy with Cloud Build (public access by default)
gcloud builds submit --config cloudbuild.yaml
```

The deployment automatically configures public access. The IAM policy binding is included in the Cloud Build configuration.

**Note**: After deployment, it may take 30-60 seconds for the service to be fully accessible.

#### Optional: Switch to IAM Authentication

If you want to restrict access to authorized users only:

```bash
# Remove public access
gcloud run services remove-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Grant access to specific users
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"
```

**To access an IAM-authenticated service:**

```bash
# Method 1: Use gcloud auth to get a token and access via curl
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" https://qrl-bot-545492969490.asia-east1.run.app/

# Method 2: Access via browser (will prompt for Google authentication)
# Just open the URL after granting yourself access
```

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
├── config.py                  # Configuration
├── exchange.py                # MEXC integration
├── main.py                   # Trading logic
├── risk.py                   # Risk checks
├── state.py                  # Position tracking
├── strategy.py               # EMA strategy
├── web/app.py                # Dashboard
├── Dockerfile                # Container image
├── cloudbuild.yaml           # Cloud Build config
├── AUTHENTICATION_GUIDE.md   # Cloud Run authentication guide
└── MEXC_API_SETUP.md        # MEXC API setup guide
```

## 📚 Documentation

- **[MEXC_API_SETUP.md](MEXC_API_SETUP.md)** - Comprehensive guide for setting up MEXC API credentials
- **[AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)** - Detailed guide for Cloud Run authentication (public vs IAM)
- **[快速開始.md](快速開始.md)** - Chinese quick start guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

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

This error means the service doesn't allow unauthenticated access. There are two solutions:

**Solution 1: Enable Public Access (for development/testing)**

```bash
# Grant public access to the service
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Verify the policy is set
gcloud run services get-iam-policy qrl-bot --region=asia-east1
```

**Solution 2: Use IAM Authentication (recommended for production)**

```bash
# Grant yourself access
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"

# Access via browser with authentication
# Or use curl with authentication token:
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" https://your-service-url.run.app/
```

**Understanding the 403 Error**:

Google Cloud Run requires explicit IAM permissions to access services:
- **Public access**: Requires `allUsers` to have the `run.invoker` role
- **Authenticated access**: Requires specific users/service accounts to have the `run.invoker` role
- The `--allow-unauthenticated` flag in deployment sets the public access policy
- If deployment doesn't include this flag or the IAM policy, you get a 403 error

**Which authentication mode should I use?**

| Mode | Use Case | Security | Command |
|------|----------|----------|---------|
| **Public** | Development, testing, public dashboards | Low - anyone can access | `--allow-unauthenticated` |
| **IAM Auth** | Production, sensitive data | High - only authorized users | `--no-allow-unauthenticated` |

**Troubleshooting 403 errors:**

1. Check current IAM policy:
```bash
gcloud run services get-iam-policy qrl-bot --region=asia-east1
```

2. If you see `allUsers` with `roles/run.invoker`, the service is public
3. If you don't see `allUsers`, the service requires authentication
4. Wait 30-60 seconds after deployment for policies to propagate

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
