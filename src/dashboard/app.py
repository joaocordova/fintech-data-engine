import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import psycopg2

# Page Config
st.set_page_config(page_title="Fintech Data Engine", layout="wide")

st.title("📈 High-Frequency Market & Sentiment Dashboard")

# Mock connection for Demo (Replace with psycopg2 in Prod)
@st.cache_data
def load_data():
    # In a real scenario, query Postgres:
    # conn = psycopg2.connect(host="postgres", database="fintech_db", user="admin", password="password")
    # df = pd.read_sql("SELECT * FROM fact_market_activity", conn)
    
    # Mock data for portability
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "event_date": dates,
        "symbol": ["AAPL"] * 50 + ["GOOGL"] * 50,
        "close_price": [150 + i + (i%5)*2 for i in range(100)],
        "volume": [1000 + i*10 for i in range(100)]
    })
    return df

df = load_data()

# Sidebar
st.sidebar.header("Filters")
selected_symbol = st.sidebar.selectbox("Select Symbol", df["symbol"].unique())

# Filter Data
filtered_df = df[df["symbol"] == selected_symbol]

# 1. Price Chart with SMA (Data Science Feature)
st.subheader(f"{selected_symbol} Price Analysis")

# Calculate SMA 20
filtered_df['SMA_20'] = filtered_df['close_price'].rolling(window=20).mean()

fig = go.Figure()
fig.add_trace(go.Scatter(x=filtered_df['event_date'], y=filtered_df['close_price'], mode='lines', name='Close Price'))
fig.add_trace(go.Scatter(x=filtered_df['event_date'], y=filtered_df['SMA_20'], mode='lines', name='SMA 20 (Trend)', line=dict(dash='dash')))

st.plotly_chart(fig, use_container_width=True)

# 2. Volume Analysis
st.subheader("Volume Traded")
fig_vol = px.bar(filtered_df, x="event_date", y="volume", title="Daily Volume")
st.plotly_chart(fig_vol, use_container_width=True)

# 3. Data Contract Status (Mock)
st.subheader("Data Quality Monitor")
col1, col2, col3 = st.columns(3)
col1.metric("Freshness", "Real-time", "0s")
col2.metric("Schema Violations", "0", "0%")
col3.metric("Data Quality Score", "99.8%", "+0.1%")
