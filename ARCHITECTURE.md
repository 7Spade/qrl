# QRL Trading Bot - Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    QRL Trading Bot System                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   main.py   │────────▶│   Modules    │────────▶│   MEXC API  │
│ (Execution) │         │              │         │  (Exchange) │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │ SQLite   │
                        │ Database │
                        └──────────┘
```

## Component Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                        Main Entry Point                        │
│                          (main.py)                             │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ 1. Fetch OHLCV → 2. Check Strategy → 3. Check Risk  │    │
│  │ 4. Calculate Price → 5. Place Order → 6. Update DB  │    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
    │  config.py  │  │  exchange.py │  │ strategy.py │
    │             │  │              │  │             │
    │ - SYMBOL    │  │ - CCXT API   │  │ - EMA20/60  │
    │ - LIMITS    │  │ - Auth       │  │ - Signals   │
    │ - OFFSET    │  │ - Rate Limit │  │ - Analysis  │
    └─────────────┘  └──────────────┘  └─────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
    │   risk.py   │  │   state.py   │  │  web/app.py │
    │             │  │              │  │             │
    │ - Position  │  │ - SQLite ORM │  │ - FastAPI   │
    │ - Limits    │  │ - Persist    │  │ - Dashboard │
    │ - Checks    │  │ - CRUD       │  │ - Monitor   │
    └─────────────┘  └──────────────┘  └─────────────┘
```

## Data Flow Diagram

```
┌──────────┐
│  Start   │
└────┬─────┘
     │
     ▼
┌─────────────────────────┐
│ Load Configuration      │
│ (config.py, .env)       │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐
│ Initialize Exchange     │
│ (exchange.py)           │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐
│ Fetch 120d OHLCV Data   │
│ from MEXC API           │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐
│ Calculate EMA20/EMA60   │
│ (strategy.py)           │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐      NO    ┌──────────┐
│ Should Buy?             │───────────▶│   Exit   │
│ (strategy.should_buy)   │            └──────────┘
└────┬────────────────────┘
     │ YES
     ▼
┌─────────────────────────┐
│ Get Current Position    │
│ (state.get_position)    │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐      NO    ┌──────────┐
│ Can Buy?                │───────────▶│   Exit   │
│ (risk.can_buy)          │            └──────────┘
└────┬────────────────────┘
     │ YES
     ▼
┌─────────────────────────┐
│ Fetch Current Price     │
│ Calculate Order Amount  │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐
│ Place Limit Buy Order   │
│ (exchange API call)     │
└────┬────────────────────┘
     │
     ▼
┌─────────────────────────┐
│ Update Position in DB   │
│ (state.update_position) │
└────┬────────────────────┘
     │
     ▼
┌──────────┐
│   Done   │
└──────────┘
```

## Module Dependencies

```
main.py
  ├── config.py
  │   ├── dotenv
  │   └── os
  ├── exchange.py
  │   ├── ccxt
  │   └── os
  ├── strategy.py
  │   ├── pandas
  │   └── ta (EMAIndicator)
  ├── risk.py
  ├── state.py
  │   ├── sqlalchemy
  │   └── os
  └── [runtime]
      ├── ccxt.fetch_ohlcv()
      ├── ccxt.fetch_ticker()
      └── ccxt.create_limit_buy_order()
```

## Database Schema

```
┌─────────────────────────┐
│      state.db           │
├─────────────────────────┤
│  Table: state           │
├─────────────────────────┤
│  Column  │  Type        │
├──────────┼──────────────┤
│  pos     │  REAL        │
│          │              │
│ Purpose: Store current  │
│ position value in USDT  │
└─────────────────────────┘

Notes:
- Single row table
- Updated on every trade
- DELETE + INSERT pattern
- No historical tracking
```

## Web Dashboard Architecture

```
┌────────────────────────────────────────┐
│         FastAPI Web Application         │
├────────────────────────────────────────┤
│                                         │
│  GET /                                  │
│  ├── Fetch QRL/USDT price (CCXT)      │
│  ├── Query position from SQLite        │
│  └── Render Jinja2 template            │
│                                         │
└────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────┐
│      templates/index.html               │
├────────────────────────────────────────┤
│  Display:                               │
│  - Symbol: QRL/USDT                     │
│  - Current Price                        │
│  - Position (USDT)                      │
│  - Last Update Timestamp                │
└────────────────────────────────────────┘
```

## Configuration Flow

```
┌──────────────┐
│ .env file    │
│              │
│ MEXC_API_KEY │
│ MEXC_SECRET  │
│ SYMBOL       │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ python-dotenv loads  │
│ env vars to os.env   │
└──────┬───────────────┘
       │
       ├──────────────────┬────────────────┐
       ▼                  ▼                ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────┐
│ config.py   │  │ exchange.py  │  │ web/app.py  │
│             │  │              │  │             │
│ SYMBOL      │  │ API_KEY      │  │ (optional)  │
│ TIMEFRAME   │  │ API_SECRET   │  │             │
│ BASE_ORDER  │  │              │  │             │
│ MAX_POS     │  │              │  │             │
│ OFFSET      │  │              │  │             │
└─────────────┘  └──────────────┘  └─────────────┘
```

## Trading Strategy Logic

```
┌────────────────────────────────────────┐
│        Strategy Evaluation              │
├────────────────────────────────────────┤
│                                         │
│  Input: 120 days OHLCV data            │
│         [timestamp, O, H, L, C, V]     │
│                                         │
│  Step 1: Convert to DataFrame          │
│         ┌──────────────────────┐       │
│         │ ts│open│high│low│... │       │
│         │ 1 │... │... │...│... │       │
│         │...│... │... │...│... │       │
│         └──────────────────────┘       │
│                                         │
│  Step 2: Calculate Indicators          │
│         df['ema20'] = EMA(close, 20)   │
│         df['ema60'] = EMA(close, 60)   │
│                                         │
│  Step 3: Get Latest Values             │
│         latest = df.iloc[-1]           │
│                                         │
│  Step 4: Evaluate Conditions           │
│         ┌─────────────────────────┐    │
│         │ close <= ema60 * 1.02   │    │
│         │        AND              │    │
│         │    ema20 >= ema60       │    │
│         └─────────────────────────┘    │
│                  │                      │
│         ┌────────┴────────┐            │
│         ▼                 ▼            │
│       TRUE              FALSE          │
│    (Buy Signal)      (No Action)       │
└────────────────────────────────────────┘
```

## Error Handling (Current State)

```
┌────────────────────────────────────────┐
│     Current Error Handling: MINIMAL     │
├────────────────────────────────────────┤
│                                         │
│  ❌ No try-catch blocks                 │
│  ❌ No logging                          │
│  ❌ No retry logic                      │
│  ❌ No API validation                   │
│  ❌ No network error handling           │
│                                         │
│  Script will crash on:                 │
│  - Network failures                    │
│  - API rate limits                     │
│  - Invalid API credentials             │
│  - Database errors                     │
│  - Exchange errors                     │
│                                         │
│  ⚠️ NEEDS IMPROVEMENT                   │
└────────────────────────────────────────┘
```

## Deployment Architecture (Recommended)

```
┌─────────────────────────────────────────────────┐
│                  Production                      │
└─────────────────────────────────────────────────┘

┌──────────────┐      ┌────────────────┐
│   Scheduler  │      │  Web Dashboard │
│   (Cron/     │      │   (uvicorn)    │
│   systemd)   │      │   Port: 8000   │
└──────┬───────┘      └────────┬───────┘
       │                       │
       ▼                       │
┌──────────────┐              │
│   main.py    │              │
│  (Trading    │              │
│   Logic)     │              │
└──────┬───────┘              │
       │                       │
       ├───────────────────────┼───────────┐
       ▼                       ▼           ▼
┌─────────────┐      ┌──────────────┐  ┌────────┐
│  MEXC API   │      │  SQLite DB   │  │  Logs  │
│  (Trading)  │      │  (State)     │  │  Dir   │
└─────────────┘      └──────────────┘  └────────┘
```

## Security Layers

```
┌────────────────────────────────────────┐
│         Security Architecture           │
├────────────────────────────────────────┤
│                                         │
│  Layer 1: Environment Variables        │
│  ├── API keys in .env                  │
│  ├── .gitignore prevents commit        │
│  └── Local file permissions            │
│                                         │
│  Layer 2: API Permissions              │
│  ├── Trading keys (main.py)            │
│  └── Read-only keys (web/app.py)       │
│                                         │
│  Layer 3: Database Security            │
│  ├── Local SQLite file                 │
│  └── File system permissions           │
│                                         │
│  Layer 4: Network Security             │
│  ├── CCXT rate limiting                │
│  └── HTTPS API calls                   │
│                                         │
│  ⚠️ Missing:                            │
│  - Input sanitization                  │
│  - Request validation                  │
│  - Web auth (dashboard)                │
└────────────────────────────────────────┘
```

## Performance Characteristics

```
┌────────────────────────────────────────┐
│      Performance Profile                │
├────────────────────────────────────────┤
│                                         │
│  Execution Time: ~2-5 seconds          │
│  ├── API calls: 1-3 seconds            │
│  ├── Calculation: <100ms               │
│  └── Database: <10ms                   │
│                                         │
│  Memory Usage: ~50-100MB               │
│  ├── Python runtime: 30-50MB           │
│  ├── Libraries: 20-40MB                │
│  └── Data: <10MB                       │
│                                         │
│  Network:                              │
│  ├── OHLCV fetch: ~5KB                 │
│  ├── Ticker fetch: ~1KB                │
│  └── Order placement: ~1KB             │
│                                         │
│  Bottlenecks:                          │
│  - Network latency (API calls)         │
│  - Rate limits (CCXT auto-handled)     │
└────────────────────────────────────────┘
```

## Scalability Considerations

```
Current Design:
- Single instance
- Synchronous execution
- Single trading pair
- Local database

Scaling Options:

1. Horizontal Scaling (Multiple Pairs)
   ├── Separate instance per pair
   └── Shared database (PostgreSQL)

2. Vertical Scaling (Resources)
   ├── More API rate limit
   └── Faster execution

3. Feature Scaling
   ├── Multiple strategies
   ├── Multiple exchanges
   └── Portfolio management
```

---

**Note**: This architecture represents the current state. See PROJECT_ANALYSIS.md for recommended improvements.
