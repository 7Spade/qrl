"""
QRL Trading Bot - Streamlit Dashboard

Main dashboard application using Streamlit for the frontend.
The FastAPI backend continues to provide API endpoints for data.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="QRL Trading Bot Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL (assumes FastAPI is running)
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0a0e27;
        color: #00ff41;
    }
    .stMetric {
        background-color: #1a1f3a;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #00ff41;
    }
    .stMetric label {
        color: #00d4ff !important;
    }
    .stMetric .metric-value {
        color: #00ff41 !important;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 QRL Trading Bot Dashboard")
st.markdown("---")

# Sidebar for timeframe selection
st.sidebar.header("⚙️ Settings")
timeframe = st.sidebar.selectbox(
    "Chart Timeframe",
    ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
    index=4  # Default to 1h
)

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=True)

def fetch_data(endpoint):
    """Fetch data from FastAPI backend"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Main dashboard layout
col1, col2, col3, col4 = st.columns(4)

# Fetch market data
market_data = fetch_data("/api/market")

if "error" not in market_data:
    with col1:
        st.metric(
            "💰 Current Price",
            f"${market_data.get('price', 0):.6f}",
            f"{market_data.get('change_24h', 0):.2f}%"
        )
    
    with col2:
        st.metric(
            "📈 EMA 20",
            f"${market_data.get('ema20', 0):.6f}"
        )
    
    with col3:
        st.metric(
            "📉 EMA 60",
            f"${market_data.get('ema60', 0):.6f}"
        )
    
    with col4:
        balances = market_data.get('balances', {})
        st.metric(
            "💼 QRL Balance",
            f"{balances.get('qrl', 0):.4f} QRL"
        )
else:
    st.warning(f"⚠️ {market_data.get('error', 'Unable to fetch market data')}")

st.markdown("---")

# Position and Balance Information
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💼 Position & Balance")
    
    stats_data = fetch_data("/api/statistics")
    
    if "error" not in stats_data:
        position_df = pd.DataFrame([
            {"Metric": "QRL Holdings", "Value": f"{market_data.get('balances', {}).get('qrl', 0):.4f} QRL"},
            {"Metric": "USDT Balance", "Value": f"${market_data.get('balances', {}).get('usdt', 0):.2f}"},
            {"Metric": "Current Position", "Value": f"${stats_data.get('current_position', 0):.2f}"},
            {"Metric": "Max Position", "Value": f"${stats_data.get('max_position_usdt', 0):.2f}"},
            {"Metric": "Available", "Value": f"${stats_data.get('available_capacity', 0):.2f}"},
            {"Metric": "Utilization", "Value": f"{stats_data.get('position_utilization_pct', 0):.1f}%"}
        ])
        st.dataframe(position_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"⚠️ {stats_data.get('error', 'Unable to fetch statistics')}")

with col_right:
    st.subheader("📊 Strategy Status")
    
    if "error" not in market_data:
        buy_threshold = market_data.get('ema60', 0) * 1.02
        buy_signal = market_data.get('buy_signal', False)
        
        status_text = '✅ Ready to Buy' if buy_signal else '⏸️ Waiting'
        st.metric("Status", status_text)
        
        st.write(f"**Buy Condition:** Price ≤ ${buy_threshold:.6f}")
        
        if "error" not in stats_data:
            st.write(f"**Last Trade:** {stats_data.get('last_trade_time', 'None')}")

st.markdown("---")

# Chart section
st.subheader(f"📈 Price Chart ({timeframe})")

chart_data = fetch_data(f"/api/market/chart-data?timeframe={timeframe}")
indicators_data = fetch_data(f"/api/market/indicators?timeframe={timeframe}")

if "error" not in chart_data and "error" not in indicators_data:
    # Create price chart with plotly
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price & Moving Averages', 'Volume', 'RSI', 'MACD'),
        row_heights=[0.5, 0.15, 0.15, 0.2]
    )
    
    labels = chart_data.get('labels', [])
    
    # Price and MAs
    fig.add_trace(go.Scatter(x=labels, y=chart_data.get('prices', []), 
                             name='Price', line=dict(color='#00ff41', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=labels, y=chart_data.get('ema20', []), 
                             name='EMA 20', line=dict(color='#ff00ff', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=labels, y=chart_data.get('ema60', []), 
                             name='EMA 60', line=dict(color='#ffff00', dash='dash')), row=1, col=1)
    
    # Volume
    fig.add_trace(go.Bar(x=labels, y=chart_data.get('volumes', []), 
                         name='Volume', marker_color='#00d4ff'), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=labels, y=indicators_data.get('rsi', []), 
                             name='RSI', line=dict(color='#00ff41')), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=labels, y=indicators_data.get('macd', []), 
                             name='MACD', line=dict(color='#00d4ff')), row=4, col=1)
    fig.add_trace(go.Scatter(x=labels, y=indicators_data.get('macd_signal', []), 
                             name='Signal', line=dict(color='#ff9500')), row=4, col=1)
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        template="plotly_dark",
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(0,255,65,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='rgba(0,255,65,0.1)')
    
    st.plotly_chart(fig, use_container_width=True)
else:
    chart_error = chart_data.get('message') or chart_data.get('error', 'Unable to fetch chart data')
    st.warning(f"⚠️ {chart_error}")

st.markdown("---")

# System status
st.subheader("🔧 System Status")

col_sys1, col_sys2, col_sys3, col_sys4 = st.columns(4)

health_data = fetch_data("/health")
cache_data = fetch_data("/api/cache/stats")

with col_sys1:
    health_status = "✅ Healthy" if health_data.get('status') == 'healthy' else "❌ Unhealthy"
    st.metric("System Health", health_status)

with col_sys2:
    api_status = "● Connected" if health_data.get('status') == 'healthy' else "⚠ Error"
    st.metric("API Connection", api_status)

with col_sys3:
    cache_status = "✅ Enabled" if cache_data.get('enabled') else "❌ Disabled"
    st.metric("Redis Cache", cache_status)

with col_sys4:
    data_delay = "< 100ms" if cache_data.get('enabled') else "200-500ms"
    st.metric("Data Delay", data_delay)

# Footer
st.markdown("---")
current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
st.caption(f"QRL Trading Bot v2.0 - Production Ready | UTC Time: {current_time}")

# Auto-refresh logic
if auto_refresh:
    time.sleep(60)
    st.rerun()
