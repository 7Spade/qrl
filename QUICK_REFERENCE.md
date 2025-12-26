# Quick Reference Guide

This is a quick reference for common tasks with the QRL Trading Bot.

## 🔑 MEXC API Setup

### Get API Credentials

1. Visit: https://www.mexc.com/user/openapi
2. Create API with "Spot Trading" permission
3. Save both credentials:
   - **Access Key** → `MEXC_API_KEY`
   - **Secret Key** → `MEXC_API_SECRET`

### Configure .env

```bash
cp .env.example .env
# Edit and fill in:
MEXC_API_KEY=your_access_key_here
MEXC_API_SECRET=your_secret_key_here
```

📖 **Full Guide**: [MEXC_API_SETUP.md](MEXC_API_SETUP.md)

---

## ☁️ Cloud Run Deployment

### Public Access (Development)

```bash
gcloud builds submit --config cloudbuild.yaml
```

Access at: `https://your-service-url.run.app`

### IAM Authentication (Production)

```bash
gcloud builds submit --config cloudbuild.yaml --substitutions _USE_IAM_AUTH=true
```

Grant yourself access:
```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"
```

📖 **Full Guide**: [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)

---

## 🔧 Common Commands

### Local Development

```bash
# Run trading bot
python main.py

# Run web dashboard
uvicorn web.app:app --reload
```

### Cloud Run Management

```bash
# Check current IAM policy
gcloud run services get-iam-policy qrl-bot --region=asia-east1

# Enable public access
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Remove public access
gcloud run services remove-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# View logs
gcloud run services logs read qrl-bot --region=asia-east1 --limit=50
```

---

## 🐛 Troubleshooting

### 403 Forbidden Error

**Quick Fix (Public Access)**:
```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

**Quick Fix (Your Access Only)**:
```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"
```

### API Connection Error

```bash
# Test API credentials
python3 << 'PYTHON'
import ccxt, os
from dotenv import load_dotenv
load_dotenv()
exchange = ccxt.mexc({
    'apiKey': os.getenv('MEXC_API_KEY'),
    'secret': os.getenv('MEXC_API_SECRET'),
})
print(exchange.fetch_balance())
PYTHON
```

### Check Service Status

```bash
# Describe service
gcloud run services describe qrl-bot --region=asia-east1

# Check recent logs
gcloud run services logs read qrl-bot --region=asia-east1 --limit=10
```

---

## 📊 Monitoring

### Access Dashboard

- **Public**: Just open the URL
- **IAM Auth**: Authenticate with Google, then access

### View Position

Dashboard shows:
- Current QRL/USDT price
- Total position value
- Last update timestamp

### Check Logs

```bash
# Recent activity
gcloud run services logs read qrl-bot --region=asia-east1

# Filter by user
gcloud run services logs read qrl-bot --region=asia-east1 \
  --filter="protoPayload.authenticationInfo.principalEmail=user@gmail.com"
```

---

## 🔐 Security Checklist

- [ ] API keys stored in `.env` (not hardcoded)
- [ ] `.env` file in `.gitignore`
- [ ] "Spot Trading" permission only (no withdrawal)
- [ ] IP binding enabled (optional but recommended)
- [ ] IAM authentication for production
- [ ] Regular API key rotation
- [ ] Monitoring enabled

---

## 📖 Full Documentation

| Guide | Purpose |
|-------|---------|
| [README.md](README.md) | Main documentation and overview |
| [MEXC_API_SETUP.md](MEXC_API_SETUP.md) | MEXC API credentials setup |
| [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) | Cloud Run authentication |
| [快速開始.md](快速開始.md) | Chinese quick start |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## 🚀 Quick Start Workflow

1. **Setup MEXC API**
   ```bash
   # Visit: https://www.mexc.com/user/openapi
   # Create API and save credentials
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Test Locally**
   ```bash
   python main.py
   ```

4. **Deploy to Cloud**
   ```bash
   # Public access (dev)
   gcloud builds submit --config cloudbuild.yaml
   
   # Or IAM auth (prod)
   gcloud builds submit --config cloudbuild.yaml --substitutions _USE_IAM_AUTH=true
   ```

5. **Grant Access (if using IAM)**
   ```bash
   gcloud run services add-iam-policy-binding qrl-bot \
     --region=asia-east1 \
     --member="user:your-email@gmail.com" \
     --role="roles/run.invoker"
   ```

6. **Monitor**
   - Open dashboard URL
   - Check logs: `gcloud run services logs read qrl-bot --region=asia-east1`

---

**Need Help?** See the full guides linked above for detailed explanations.
