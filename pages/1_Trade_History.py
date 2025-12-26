"""Trade History Page for QRL Trading Bot"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Trade History", page_icon="📜", layout="wide")

API_BASE_URL = "http://localhost:8000"

st.title("📜 Trade History")
st.markdown("---")

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

# Fetch trade history
limit = st.sidebar.slider("Number of trades", 10, 100, 50)
trades_data = fetch_data(f"/api/trades?limit={limit}")

if "error" not in trades_data and "trades" in trades_data:
    trades = trades_data["trades"]
    
    if trades:
        # Convert to DataFrame
        df = pd.DataFrame(trades)
        
        # Format columns
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", len(trades))
        
        with col2:
            total_amount = df['amount'].sum() if 'amount' in df.columns else 0
            st.metric("Total Amount", f"{total_amount:.4f} QRL")
        
        with col3:
            avg_price = df['price'].mean() if 'price' in df.columns else 0
            st.metric("Average Price", f"${avg_price:.6f}")
        
        with col4:
            total_cost = df['cost'].sum() if 'cost' in df.columns else 0
            st.metric("Total Cost", f"${total_cost:.2f}")
        
        st.markdown("---")
        
        # Display trade table
        st.subheader("Recent Trades")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"qrl_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No trades found")
else:
    st.error(f"⚠️ {trades_data.get('error', 'Unable to fetch trade history')}")

st.markdown("---")

# Statistics
st.subheader("📊 Trading Statistics")

stats_data = fetch_data("/api/statistics")

if "error" not in stats_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Position Metrics**")
        position_df = pd.DataFrame([
            {"Metric": "Current Position", "Value": f"${stats_data.get('current_position', 0):.2f}"},
            {"Metric": "Max Position", "Value": f"${stats_data.get('max_position_usdt', 0):.2f}"},
            {"Metric": "Available Capacity", "Value": f"${stats_data.get('available_capacity', 0):.2f}"},
            {"Metric": "Position Utilization", "Value": f"{stats_data.get('position_utilization_pct', 0):.1f}%"}
        ])
        st.dataframe(position_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**Trade Metrics**")
        trade_df = pd.DataFrame([
            {"Metric": "Total Trades", "Value": stats_data.get('total_trades', 0)},
            {"Metric": "Total Cost", "Value": f"${stats_data.get('total_cost', 0):.2f}"},
            {"Metric": "Average Price", "Value": f"${stats_data.get('avg_price', 0):.6f}"},
            {"Metric": "Last Trade", "Value": stats_data.get('last_trade_time', 'N/A')}
        ])
        st.dataframe(trade_df, use_container_width=True, hide_index=True)

st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
