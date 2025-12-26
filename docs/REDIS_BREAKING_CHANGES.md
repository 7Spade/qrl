# Redis Breaking Changes - v2.0

## Overview

Based on feedback about technical debt accumulation, Redis caching is now **REQUIRED** for trading bot operation. This change eliminates fallback behavior and ensures consistent, high-performance operation.

## Breaking Changes

### 1. Redis is Now REQUIRED

**Before (v1.x):**
```python
# Optional - bot would run without Redis
cache_config = CacheConfig(redis_url=None, redis_enabled=False)
```

**After (v2.0):**
```python
# REQUIRED - bot will fail to start without valid Redis connection
cache_config = CacheConfig(redis_url="redis://host:port")  # Must be valid
```

**Impact:**
- Application will **fail to start** if `REDIS_URL` is not set
- No fallback behavior - Redis must be running and accessible
- Clear error messages guide users to configure Redis properly

### 2. CacheConfig Changes

**Removed Fields:**
- `redis_enabled: bool` - Redis is always enabled now
- All optional redis_url behavior

**Required Fields:**
- `redis_url: str` - Must be a valid Redis connection URL (no longer Optional)

### 3. CacheClient Behavior Changes

**Before:**
- Methods returned `False` or `None` when Redis unavailable
- Graceful degradation to no-cache mode
- `enabled` property to check if cache is working

**After:**
- Methods raise `RuntimeError` when Redis operations fail
- No silent failures - errors are explicit
- Automatic reconnection attempts on transient failures
- No `enabled` property - Redis is always required

**Example:**
```python
# Before (v1.x)
result = cache.set("key", "value")
if not result:
    print("Cache failed, continuing anyway...")

# After (v2.0)
try:
    cache.set("key", "value")
except RuntimeError as e:
    # Critical failure - cannot continue without Redis
    logger.error(f"Redis operation failed: {e}")
    raise
```

### 4. ExchangeClient Changes

**Before:**
```python
# cache_config was optional
exchange_client = ExchangeClient(config, cache_config=None)
```

**After:**
```python
# cache_config is REQUIRED
cache_config = CacheConfig.from_env()  # Raises if REDIS_URL not set
exchange_client = ExchangeClient(config, cache_config)
```

### 5. Environment Variables

**Before (.env):**
```bash
# REDIS_URL=redis://host:port  # Commented out = optional
```

**After (.env):**
```bash
REDIS_URL=redis://host:port  # REQUIRED - must be uncommented and valid
```

## Migration Guide

### Step 1: Install Redis

If you don't have Redis running:

**Option A: Local Redis (development)**
```bash
# Docker
docker run -d -p 6379:6379 redis:latest

# Or install locally
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
brew services start redis
```

**Option B: Cloud Redis (production)**
- Redis Labs: https://redis.com/try-free/
- AWS ElastiCache
- Google Cloud Memorystore
- Azure Cache for Redis

### Step 2: Update .env File

```bash
# REQUIRED: Set valid Redis URL
REDIS_URL=redis://localhost:6379

# Optional: Customize TTLs
REDIS_CACHE_TTL=60
REDIS_CACHE_TTL_TICKER=5
REDIS_CACHE_TTL_OHLCV=60
REDIS_CACHE_TTL_DEALS=10
REDIS_CACHE_TTL_ORDERBOOK=5

# Optional: Set namespace for environment isolation
REDIS_NAMESPACE=qrl
```

### Step 3: Update Code

**Remove Optional Cache Checks:**

```python
# REMOVE THIS (v1.x)
if cache_client and cache_client.enabled:
    data = cache_client.get("key")

# USE THIS (v2.0)
data = cache_client.get("key")
```

**Update Error Handling:**

```python
# REMOVE THIS (v1.x)
success = cache_client.set("key", value)
if not success:
    logger.warning("Cache write failed")

# USE THIS (v2.0)
try:
    cache_client.set("key", value)
except RuntimeError as e:
    logger.error(f"Cache write failed: {e}")
    # This is a critical error - handle appropriately
    raise
```

**Update ExchangeClient Initialization:**

```python
# REMOVE THIS (v1.x)
exchange_client = ExchangeClient(
    exchange_config,
    cache_config=None  # Optional
)

# USE THIS (v2.0)
cache_config = CacheConfig.from_env()  # Will raise if REDIS_URL not set
exchange_client = ExchangeClient(exchange_config, cache_config)
```

### Step 4: Update Tests

Mock Redis in tests instead of relying on fallback behavior:

```python
# v2.0 Test Pattern
from unittest.mock import patch, MagicMock

def test_my_function():
    with patch('redis.from_url') as mock_from_url:
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_from_url.return_value = mock_redis
        
        config = CacheConfig(redis_url="redis://localhost:6379")
        client = CacheClient(config)
        
        # Your test code here
```

## Rationale

### Why Make Redis Required?

1. **Eliminates Technical Debt**: No more dual-code paths (with/without cache)
2. **Better Performance**: Always use high-performance caching
3. **Simpler Code**: No conditional cache checks throughout codebase
4. **Fail Fast**: Clear errors at startup vs. degraded performance in production
5. **Better Testing**: Forces proper Redis mocking in tests

### Why No Backward Compatibility?

As requested: "從本質修正不要向後兼容,一堆技術債了還是學不到教訓呢你" (Fix from the essence, don't maintain backward compatibility, there's already a pile of technical debt)

- Backward compatibility perpetuates technical debt
- Clean break allows proper architecture
- Migration is one-time cost vs. ongoing maintenance burden
- Clear error messages make migration straightforward

## Rollback Plan

If you need to rollback to v1.x behavior:

```bash
git checkout <previous-commit-hash>
```

Or pin to v1.x in requirements:
```bash
# Not recommended - upgrade to v2.0 instead
```

## Troubleshooting

### Error: "REDIS_URL environment variable is required"

**Solution:** Set REDIS_URL in your .env file:
```bash
REDIS_URL=redis://localhost:6379
```

### Error: "Failed to connect to Redis"

**Solution:** Ensure Redis is running:
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# If not running, start Redis
docker run -d -p 6379:6379 redis:latest
```

### Error: "Redis library not installed"

**Solution:** Install Redis Python client:
```bash
pip install redis
# Or
pip install -r requirements.txt
```

## Support

For issues or questions:
- Check [REDIS_IMPROVEMENTS.md](./REDIS_IMPROVEMENTS.md) for detailed implementation
- Review [README.md](../README.md) for configuration examples
- Open an issue on GitHub

---

**Version:** 2.0.0  
**Date:** 2024-12-26  
**Breaking Change Level:** Major (requires Redis installation and configuration)
