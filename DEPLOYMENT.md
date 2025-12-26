# QRL Trading Bot - Google Cloud Run Deployment Guide

## Overview

This guide covers deploying the QRL Trading Bot to Google Cloud Run for the web dashboard, plus scheduling the trading bot execution.

## Architecture

```
┌─────────────────────────────────────────┐
│      Google Cloud Run (Web Dashboard)   │
│      - FastAPI application              │
│      - Real-time price monitoring       │
│      - Position tracking                │
│      - Port: 8080                       │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Cloud Scheduler (Trading Bot)      │
│      - Runs main.py periodically        │
│      - Executes trading logic           │
│      - Updates SQLite database          │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Cloud Storage (Persistent Data)    │
│      - SQLite database backup           │
│      - Trade history logs               │
└─────────────────────────────────────────┘
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured
3. **Docker** installed (for local testing)
4. **MEXC API Keys** (trading and read-only)

## Quick Start

### 1. Setup Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="asia-east1"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com
```

### 2. Store API Keys in Secret Manager

```bash
# Store MEXC API credentials securely
echo -n "your-api-key" | gcloud secrets create mexc-api-key \
  --data-file=- \
  --replication-policy="automatic"

echo -n "your-api-secret" | gcloud secrets create mexc-api-secret \
  --data-file=- \
  --replication-policy="automatic"
```

### 3. Build and Deploy with Cloud Build

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or manually build and deploy
docker build -t gcr.io/$PROJECT_ID/qrl-bot:latest .
docker push gcr.io/$PROJECT_ID/qrl-bot:latest

gcloud run deploy qrl-bot \
  --image gcr.io/$PROJECT_ID/qrl-bot:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-secrets=MEXC_API_KEY=mexc-api-key:latest,MEXC_API_SECRET=mexc-api-secret:latest \
  --set-env-vars=SYMBOL=QRL/USDT
```

### 4. Setup Cloud Scheduler for Trading Bot

```bash
# Get the Cloud Run service URL
SERVICE_URL=$(gcloud run services describe qrl-bot \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

# Create a Cloud Scheduler job (runs daily at 9 AM UTC+8)
gcloud scheduler jobs create http qrl-bot-trader \
  --location=$REGION \
  --schedule="0 9 * * *" \
  --uri="$SERVICE_URL/trade" \
  --http-method=POST \
  --oidc-service-account-email=qrl-bot@$PROJECT_ID.iam.gserviceaccount.com \
  --time-zone="Asia/Taipei"
```

### 5. Access Your Dashboard

```bash
# Get the service URL
gcloud run services describe qrl-bot \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)'
```

Visit the URL in your browser to see the dashboard!

## Local Testing

### Test with Docker

```bash
# Build the image
docker build -t qrl-bot .

# Run the web dashboard
docker run -p 8080:8080 \
  -e MEXC_API_KEY="your-key" \
  -e MEXC_API_SECRET="your-secret" \
  qrl-bot

# Run the trading bot (one-time execution)
docker run \
  -e MEXC_API_KEY="your-key" \
  -e MEXC_API_SECRET="your-secret" \
  qrl-bot python main.py
```

### Test with Docker Compose

```bash
# Create .env file with your credentials
cp .env.example .env
# Edit .env and add your API keys

# Start the web dashboard
docker-compose up qrl-bot-web

# Run the trading bot (one-time)
docker-compose run --rm qrl-bot-trader
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MEXC_API_KEY` | Yes | - | MEXC API key |
| `MEXC_API_SECRET` | Yes | - | MEXC API secret |
| `SYMBOL` | No | `QRL/USDT` | Trading pair |
| `PORT` | No | `8080` | Web server port |

### Cloud Run Settings

Recommended configuration for production:

```bash
gcloud run deploy qrl-bot \
  --image gcr.io/$PROJECT_ID/qrl-bot:latest \
  --platform managed \
  --region asia-east1 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --concurrency 80 \
  --timeout 300 \
  --allow-unauthenticated
```

## Persistent Storage

Cloud Run is stateless. For persistent SQLite database:

### Option 1: Cloud Storage (Recommended)

```bash
# Create a bucket
gsutil mb gs://$PROJECT_ID-qrl-data

# Mount in Cloud Run (requires Cloud Run with Cloud Storage)
# Add volume mount in deployment
```

### Option 2: Cloud SQL

For production-grade persistence:

```bash
# Create Cloud SQL instance
gcloud sql instances create qrl-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION

# Update code to use PostgreSQL instead of SQLite
```

## Monitoring

### View Logs

```bash
# View Cloud Run logs
gcloud run logs read qrl-bot --region=$REGION

# Follow logs in real-time
gcloud run logs tail qrl-bot --region=$REGION
```

### Setup Alerts

```bash
# Create an alert for errors
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="QRL Bot Errors" \
  --condition-display-name="Error rate high" \
  --condition-threshold-value=0.1 \
  --condition-threshold-duration=60s
```

## Cost Optimization

1. **Use minimum resources**: 256Mi RAM, 0.5 CPU for dashboard
2. **Set min instances to 0**: Pay only when running
3. **Use Cloud Scheduler carefully**: Limit trading frequency
4. **Monitor API calls**: MEXC has rate limits

**Estimated Monthly Cost:**
- Cloud Run: $0-5 (mostly free tier)
- Cloud Scheduler: $0.10/job
- Cloud Build: $0 (120 builds/day free)
- Secret Manager: $0.06 per secret
- **Total: ~$1-10/month**

## Security Best Practices

1. ✅ Use Secret Manager for API keys
2. ✅ Enable Cloud Armor for DDoS protection
3. ✅ Use VPC Service Controls
4. ✅ Enable audit logging
5. ✅ Use read-only API keys for dashboard
6. ✅ Implement rate limiting
7. ✅ Regular security scans

## Troubleshooting

### Container fails to start

```bash
# Check logs
gcloud run logs read qrl-bot --limit=50

# Test locally first
docker run -p 8080:8080 qrl-bot
```

### Database errors

```bash
# Ensure data directory exists
# Check file permissions
# Verify SQLite compatibility
```

### API authentication fails

```bash
# Verify secrets
gcloud secrets versions access latest --secret=mexc-api-key

# Test API keys locally
python -c "from exchange import get_exchange; print(get_exchange().fetch_ticker('QRL/USDT'))"
```

## Advanced: CI/CD Pipeline

### Automatic Deployment on Git Push

```bash
# Connect repository to Cloud Build
gcloud builds triggers create github \
  --repo-name=qrl \
  --repo-owner=7Spade \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

### Multi-Environment Setup

```bash
# Deploy to staging
gcloud run deploy qrl-bot-staging \
  --image gcr.io/$PROJECT_ID/qrl-bot:$VERSION \
  --region=$REGION

# Deploy to production
gcloud run deploy qrl-bot-prod \
  --image gcr.io/$PROJECT_ID/qrl-bot:$VERSION \
  --region=$REGION
```

## Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete qrl-bot --region=$REGION

# Delete Cloud Scheduler job
gcloud scheduler jobs delete qrl-bot-trader --location=$REGION

# Delete secrets
gcloud secrets delete mexc-api-key
gcloud secrets delete mexc-api-secret

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/qrl-bot
```

## Support

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [QRL Bot Issues](https://github.com/7Spade/qrl/issues)

---

**Note**: Always test thoroughly in a development environment before deploying to production with real funds.
