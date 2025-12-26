# Redis Cache Setup Guide

## Overview

The QRL trading bot supports optional Redis caching for improved performance. Redis is **not required** for basic operation - the bot works fine without it.

## Benefits of Redis Cache

- ✅ Faster repeated market data queries
- ✅ Reduced API calls to exchange
- ✅ Lower latency for dashboard
- ✅ Shared cache across multiple instances (if needed)

## Setup Instructions

### Step 1: Get Redis URL

You can use:
- **Redis Cloud** (Free tier available): https://redis.com/try-free/
- **Local Redis**: Install locally with `brew install redis` or `apt-get install redis`
- **Other providers**: AWS ElastiCache, Google Cloud Memorystore, etc.

### Step 2: Configure Environment Variable

Add to your `.env` file:

```bash
# Redis Configuration
REDIS_URL=redis://default:password@your-redis-host:port
REDIS_CACHE_TTL=60
```

**Example with Redis Cloud**:
```bash
REDIS_URL=redis://default:123123@redis-18847.c334.asia-southeast2-1.gce.cloud.redislabs.com:18847
REDIS_CACHE_TTL=60
```

**Example with local Redis**:
```bash
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=60
```

### Step 3: Install Redis Python Library

```bash
pip install redis
```

Or uncomment the line in `requirements.txt` and run:
```bash
pip install -r requirements.txt
```

### Step 4: Verify Connection

The bot will automatically try to connect to Redis when it starts. You'll see:

✅ **Success**: `✅ Redis connected: redis-18847.c334.asia-southeast2-1.gce.cloud.redislabs.com:18847`

⚠️ **Failure**: `⚠️ Redis connection failed: [error message]`

If connection fails, the bot continues to work normally without caching.

## Usage in Code

### Basic Cache Operations

```python
from src.core.config import AppConfig
from src.data.cache import CacheClient

# Initialize cache
config = AppConfig.load()
cache = CacheClient(config.cache)

# Check if enabled
if cache.enabled:
    print("✅ Cache is active")

# Store data
cache.set("market:QRL:price", {"price": 0.45, "timestamp": "2025-12-26"}, ttl=60)

# Retrieve data
data = cache.get("market:QRL:price")
if data:
    print(f"Cached price: {data['price']}")

# Delete data
cache.delete("market:QRL:price")

# Get cache statistics
stats = cache.get_stats()
print(f"Cache keys: {stats.get('keys', 0)}")
```

### Cache Key Naming Convention

Use descriptive, namespaced keys:

```
market:{symbol}:ticker
market:{symbol}:ohlcv:{timeframe}
position:{symbol}
trades:recent:{limit}
statistics:summary
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | None | Redis connection URL |
| `REDIS_CACHE_TTL` | 60 | Default TTL in seconds |

## Troubleshooting

### Connection Refused
```
⚠️ Redis connection failed: Connection refused
```
**Solution**: Check if Redis server is running and URL is correct.

### Authentication Failed
```
⚠️ Redis connection failed: invalid password
```
**Solution**: Verify password in REDIS_URL is correct.

### Module Not Found
```
⚠️ Redis library not installed. Run: pip install redis
```
**Solution**: Install redis library: `pip install redis`

## Performance Tips

1. **Appropriate TTL**: Set TTL based on data freshness needs
   - Market prices: 5-30 seconds
   - Historical data: 5-60 minutes
   - Statistics: 1-5 minutes

2. **Selective Caching**: Only cache frequently accessed data
   - ✅ Cache: Current price, recent trades, statistics
   - ❌ Don't cache: One-time queries, user-specific data

3. **Monitor Memory**: Use `cache.get_stats()` to check memory usage

## Security

- ✅ Use strong passwords in Redis URL
- ✅ Use TLS/SSL for production: `rediss://` (note the double 's')
- ✅ Don't commit `.env` file with credentials
- ✅ Use environment variables or secret managers

## Disabling Redis

To disable Redis caching:

1. Remove or comment out `REDIS_URL` in `.env`
2. The bot will automatically run without caching

No code changes needed - cache operations gracefully degrade when Redis is unavailable.

---

**Version**: 2.0.0
**Last Updated**: 2025-12-26
