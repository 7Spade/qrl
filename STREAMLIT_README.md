# QRL Trading Bot - Streamlit Frontend

## Overview

The QRL Trading Bot now uses **Streamlit** for the frontend dashboard, providing an interactive and modern UI for monitoring your trading bot.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Frontend                      │
│         (Port 8501 - streamlit_app.py)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Dashboard   │  │    Trade     │  │   Settings   │ │
│  │    Page      │  │   History    │  │     Page     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓ HTTP Requests
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│                    (web/app.py)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  /api/market │  │  /api/trades │  │ /api/stats   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│          Trading Engine & Data Layer                     │
│    (Exchange Client, Redis Cache, State Manager)        │
└─────────────────────────────────────────────────────────┘
```

## Running the Application

### 1. Start FastAPI Backend (API Server)

The FastAPI backend must be running to provide data to the Streamlit frontend.

```bash
# Terminal 1 - Start FastAPI
uvicorn web.app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Streamlit Frontend (UI)

```bash
# Terminal 2 - Start Streamlit
streamlit run streamlit_app.py
```

The Streamlit dashboard will be available at: **http://localhost:8501**

## Features

### Main Dashboard (`streamlit_app.py`)
- 📊 Real-time price and market data
- 📈 Interactive charts with Plotly
  - Price chart with EMA indicators
  - Volume chart
  - RSI indicator
  - MACD indicator
- 💼 Account balances (QRL, USDT)
- 📊 Trading strategy status
- 🔧 System health monitoring
- ⚙️ Timeframe selection (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- 🔄 Auto-refresh every 60 seconds

### Trade History Page (`pages/1_Trade_History.py`)
- 📜 Complete trade history
- 📊 Trading statistics
- 📥 CSV export functionality
- 📈 Performance metrics

## Configuration

### Streamlit Theme

The Streamlit theme is configured in `.streamlit/config.toml` to match the QRL Trading Bot's dark theme with green accents:

```toml
[theme]
primaryColor = "#00ff41"      # Neon green
backgroundColor = "#0a0e27"    # Dark blue
secondaryBackgroundColor = "#1a1f3a"  # Slightly lighter blue
textColor = "#00ff41"          # Neon green
font = "monospace"
```

### API Connection

By default, Streamlit connects to the FastAPI backend at `http://localhost:8000`. 

To change this, edit the `API_BASE_URL` in:
- `streamlit_app.py`
- `pages/1_Trade_History.py`

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start both services
# Terminal 1: FastAPI
uvicorn web.app:app --port 8000

# Terminal 2: Streamlit
streamlit run streamlit_app.py
```

### Production Deployment

For production, you can deploy both services separately:

#### Option 1: Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'
services:
  fastapi:
    build: .
    command: uvicorn web.app:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=${REDIS_URL}
      - MEXC_API_KEY=${MEXC_API_KEY}
      - MEXC_API_SECRET=${MEXC_API_SECRET}
  
  streamlit:
    build: .
    command: streamlit run streamlit_app.py
    ports:
      - "8501:8501"
    depends_on:
      - fastapi
    environment:
      - API_BASE_URL=http://fastapi:8000
```

#### Option 2: Separate Deployments

Deploy FastAPI and Streamlit as separate services on Cloud Run or similar platforms.

**FastAPI (Backend)**:
```bash
# Port 8000
CMD uvicorn web.app:app --host 0.0.0.0 --port 8000
```

**Streamlit (Frontend)**:
```bash
# Port 8501
CMD streamlit run streamlit_app.py
```

## Advantages of Streamlit

### ✅ Benefits over HTML/JavaScript

1. **Pure Python**: No need to write JavaScript, HTML, or CSS
2. **Rapid Development**: Build interactive dashboards in minutes
3. **Built-in Components**: Charts, tables, metrics, and widgets included
4. **Auto-reload**: Changes reflect immediately during development
5. **State Management**: Streamlit handles state automatically
6. **Responsive**: Mobile-friendly by default
7. **Easy Deployment**: Simple deployment to Streamlit Cloud or containers

### 📊 Interactive Features

- **Real-time updates**: Auto-refresh every 60 seconds
- **Timeframe selection**: Switch between different chart timeframes
- **CSV Export**: Download trade history
- **Responsive charts**: Zoom, pan, and hover for details
- **Dark theme**: Matches the QRL Trading Bot aesthetic

## File Structure

```
.
├── streamlit_app.py          # Main dashboard page
├── pages/
│   └── 1_Trade_History.py    # Trade history page
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── web/
│   ├── app.py                 # FastAPI backend (unchanged)
│   ├── static/                # (Legacy - not used by Streamlit)
│   └── views/                 # (Legacy - not used by Streamlit)
├── requirements.txt           # Updated with streamlit, plotly
└── STREAMLIT_README.md        # This file
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run streamlit_app.py --server.port 8502
```

### Connection Error to FastAPI

Make sure the FastAPI backend is running on port 8000:

```bash
curl http://localhost:8000/health
```

### Cache Issues

Clear Streamlit cache:

```bash
streamlit cache clear
```

## Next Steps

1. ✅ **Start both services** (FastAPI + Streamlit)
2. ✅ **Open browser** to http://localhost:8501
3. ✅ **Monitor your trading bot** with the new interactive dashboard
4. 🚀 **Deploy to production** when ready

## Support

For issues or questions:
1. Check FastAPI logs (Terminal 1)
2. Check Streamlit logs (Terminal 2)
3. Ensure Redis is running and accessible
4. Verify MEXC API credentials are configured

---

**QRL Trading Bot v2.0** - Streamlit Edition 🚀
