# Cloud Run Authentication Guide

This guide explains how to configure authentication for your QRL Trading Bot deployed on Google Cloud Run.

## Overview

Google Cloud Run supports two authentication modes:

1. **Public Access** - Anyone with the URL can access the service (no authentication)
2. **IAM Authentication** - Only authorized Google Cloud users can access (requires authentication)

## Deployment

### Deploy with Public Access (Default)

```bash
gcloud builds submit --config cloudbuild.yaml
```

**Characteristics:**
- ✅ Easy to access - just open the URL in a browser
- ✅ Good for demos and public dashboards
- ⚠️ No access control - anyone can view your dashboard
- ⚠️ Less secure - consider IAM auth for production

The deployment automatically grants public access by:
1. Deploying with `--allow-unauthenticated` flag
2. Adding an explicit IAM policy binding for `allUsers`

### Switch to IAM Authentication (For Production)

After deploying, you can switch to IAM authentication:

```bash
# Remove public access
gcloud run services remove-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Grant yourself access
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"
```

**Characteristics:**
- ✅ Secure - only authorized users can access
- ✅ Audit trail - Google Cloud logs all access
- ✅ Fine-grained control - grant access per user/service account
- ⚠️ Requires Google Cloud authentication to access

## Accessing IAM-Authenticated Services

### Method 1: Browser with Authentication

1. Grant yourself the invoker role:

```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"
```

2. Access the URL in your browser - you'll be prompted to authenticate with your Google account

3. After authentication, you'll see the dashboard

### Method 2: Command Line with Token

```bash
# Get an authentication token
TOKEN=$(gcloud auth print-identity-token)

# Use curl with the token
curl -H "Authorization: Bearer $TOKEN" https://qrl-bot-545492969490.asia-east1.run.app/

# Or use the token in your application
```

### Method 3: Service Account (for Automation)

For automated access (e.g., monitoring systems, CI/CD):

1. Create a service account:

```bash
gcloud iam service-accounts create qrl-bot-client \
  --display-name="QRL Bot Client"
```

2. Grant the service account access:

```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="serviceAccount:qrl-bot-client@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

3. Use the service account key to authenticate in your application

## Switching Authentication Modes

### From Public to IAM Authentication

```bash
# Method 1: Remove public access
gcloud run services remove-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Then grant access to specific users
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"
```

### From IAM Authentication to Public

```bash
# Grant public access
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

## Troubleshooting

### "403 Forbidden" Error

This error means the service requires authentication but you're not authorized.

**Solution 1: Grant yourself access**

```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:your-email@gmail.com" \
  --role="roles/run.invoker"
```

**Solution 2: Enable public access**

```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Check Current IAM Policy

```bash
# View current IAM policy
gcloud run services get-iam-policy qrl-bot --region=asia-east1

# Example output for public access:
# bindings:
# - members:
#   - allUsers
#   role: roles/run.invoker

# Example output for IAM auth:
# bindings:
# - members:
#   - user:you@gmail.com
#   role: roles/run.invoker
```

### "Invalid authentication credentials" Error

Your authentication token may have expired. Re-authenticate:

```bash
gcloud auth login
TOKEN=$(gcloud auth print-identity-token)
```

## Security Best Practices

### For Development/Testing
- ✅ Use public access for convenience
- ✅ Use a separate project or test environment
- ⚠️ Don't store sensitive data in public services

### For Production
- ✅ Use IAM authentication
- ✅ Grant least-privilege access (only to users who need it)
- ✅ Use service accounts for automated access
- ✅ Enable Cloud Audit Logs to track access
- ✅ Regularly review IAM policies

### API Keys and Secrets
- ✅ Store MEXC API keys in Google Secret Manager
- ✅ Never commit API keys to source control
- ✅ Use different API keys for dev/prod environments
- ✅ Rotate API keys regularly

## Advanced Configuration

### Grant Access to Multiple Users

```bash
# Grant access to multiple users
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:user1@gmail.com" \
  --role="roles/run.invoker"

gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="user:user2@gmail.com" \
  --role="roles/run.invoker"
```

### Grant Access to a Google Group

```bash
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="group:traders@yourdomain.com" \
  --role="roles/run.invoker"
```

### Use Domain-Wide Access

```bash
# Allow all users in your domain
gcloud run services add-iam-policy-binding qrl-bot \
  --region=asia-east1 \
  --member="domain:yourdomain.com" \
  --role="roles/run.invoker"
```

## Monitoring Access

### View Access Logs

```bash
# View Cloud Run logs
gcloud run services logs read qrl-bot --region=asia-east1 --limit=50

# Filter for specific user
gcloud run services logs read qrl-bot --region=asia-east1 \
  --filter="protoPayload.authenticationInfo.principalEmail=user@gmail.com"
```

### Set Up Alerts

Create a Cloud Monitoring alert for unauthorized access attempts:

```bash
# This requires setting up Cloud Monitoring
# See: https://cloud.google.com/monitoring/alerts
```

## Summary

| Feature | Public Access | IAM Authentication |
|---------|--------------|-------------------|
| **Deployment** | Default (automatic) | Switch after deployment |
| **Access** | Anyone with URL | Authorized users only |
| **Security** | Low | High |
| **Ease of Use** | Easy | Requires auth setup |
| **Use Case** | Dev/Testing/Demos | Production/Sensitive |
| **Cost** | Same as IAM auth | Same as public |

Choose the authentication mode that best fits your security requirements and use case.
