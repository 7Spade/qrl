#!/bin/bash
# QRL Trading Bot - Quick Deployment Script for Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}QRL Trading Bot - Cloud Run Deployment${NC}"
echo "========================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}No project set. Please enter your Google Cloud Project ID:${NC}"
    read -r PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo -e "${GREEN}Using project: $PROJECT_ID${NC}"

# Set region
REGION=${REGION:-asia-east1}
echo -e "${GREEN}Using region: $REGION${NC}"

# Enable required APIs
echo -e "${YELLOW}Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com \
    run.googleapis.com \
    cloudscheduler.googleapis.com \
    secretmanager.googleapis.com

# Check if secrets exist
echo -e "${YELLOW}Checking API key secrets...${NC}"
if ! gcloud secrets describe mexc-api-key &> /dev/null; then
    echo -e "${YELLOW}Secret 'mexc-api-key' not found.${NC}"
    echo "Please enter your MEXC API Key:"
    read -rs MEXC_KEY
    echo -n "$MEXC_KEY" | gcloud secrets create mexc-api-key \
        --data-file=- \
        --replication-policy="automatic"
    echo -e "${GREEN}API Key secret created${NC}"
fi

if ! gcloud secrets describe mexc-api-secret &> /dev/null; then
    echo -e "${YELLOW}Secret 'mexc-api-secret' not found.${NC}"
    echo "Please enter your MEXC API Secret:"
    read -rs MEXC_SECRET
    echo -n "$MEXC_SECRET" | gcloud secrets create mexc-api-secret \
        --data-file=- \
        --replication-policy="automatic"
    echo -e "${GREEN}API Secret secret created${NC}"
fi

# Build and deploy
echo -e "${YELLOW}Building and deploying to Cloud Run...${NC}"
gcloud builds submit --config cloudbuild.yaml

echo -e "${GREEN}Deployment complete!${NC}"

# Get service URL
SERVICE_URL=$(gcloud run services describe qrl-bot \
    --platform managed \
    --region "$REGION" \
    --format 'value(status.url)' 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}Your QRL Bot dashboard is available at:${NC}"
    echo -e "${GREEN}$SERVICE_URL${NC}"
else
    echo -e "${YELLOW}Service URL not available yet. Check Cloud Console.${NC}"
fi

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Visit the dashboard URL above"
echo "2. Setup Cloud Scheduler for automatic trading (see DEPLOYMENT.md)"
echo "3. Monitor logs: gcloud run logs tail qrl-bot --region=$REGION"
