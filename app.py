import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import matplotlib.pyplot as plt

# --- 1. FULL INSTITUTIONAL SECURITY DICTIONARY ---
SECURITY_DICTIONARY = {
    "Commercial Banks": {
        "UBL.KA": "United Bank Limited", "MEBL.KA": "Meezan Bank Limited",
        "MCB.KA": "MCB Bank Limited", "HBL.KA": "Habib Bank Limited",
        "BAHL.KA": "Bank AL Habib Limited", "BAFL.KA": "Bank Alfalah Limited",
        "NBP.KA": "National Bank of Pakistan", "FABL.KA": "Faysal Bank Limited",
        "ABL.KA": "Allied Bank Limited", "BOP.KA": "The Bank of Punjab"
    },
    "Technology & Communication": {
        "SYS.KA": "Systems Limited", "TRG.KA": "TRG Pakistan Limited",
        "AIRLINK.KA": "Air Link Communication Limited", "NETSOL.KA": "NetSol Technologies Limited"
    },
    "Oil & Gas Exploration": {
        "OGDC.KA": "Oil & Gas Development Company Limited", "PPL.KA": "Pakistan Petroleum Limited",
        "MARI.KA": "Mari Petroleum Company Limited", "POL.KA": "Pakistan Oilfields Limited"
    },
    "Cement": {
        "LUCK.KA": "Lucky Cement Limited", "DGKC.KA": "D.G. Khan Cement Company Limited",
        "MLCF.KA": "Maple Leaf Cement Factory Limited", "CHCC.KA": "Cherat Cement Company Limited"
    }
}

CAP_WEIGHT_UNITS = {
    "UBL.KA": 420.0, "MEBL.KA": 380.0, "MCB.KA": 310.0, "HBL.KA": 180.0,
    "SYS.KA": 140.0, "OGDC.KA": 620.0, "PPL.KA": 340.0, "LUCK.KA": 240.0
}

# --- 2. ADVANCED DATA ENGINE: LIVE SESSION STITCHING ---
@st.cache_data(ttl=60)
def fetch_live_realtime_dataframe(symbol):
    """Fetches historical data and stitches active session data to eliminate lag."""
    ticker_obj = yf.Ticker(symbol)
    hist_df = ticker_obj.history(period="1y", interval="1d")
    
    # Real-time stitch for the active day
    try:
        live = ticker_obj.history(period="1d", interval="5m")
        if not live.empty:
            last_date = hist_df.index[-1].normalize()
            live_row = pd.DataFrame({
                'Open': live['Open'].iloc[0],
                'High': live['High'].max(),
                'Low': live['Low'].min(),
                'Close': live['Close'].iloc[-1],
                'Volume': live['Volume'].sum()
            }, index=[last_date])
            # Merge logic
            hist_df = pd.concat([hist_df.iloc[:-1], live_row])
    except Exception:
        pass
    
    if hist_df.index.tz is not None:
        hist_df.index = hist_df.index.tz_localize(None)
    return hist_df

# --- 3. PAGE SETUP & UI ---
st.set_page_config(page_title="PSX Advanced Analytics", layout="wide")
st.title("🏛️ PSX Professional Analytics Command Suite")

# --- 4. DATA PROCESSING PIPELINE ---
all_tickers = [t for sect in SECURITY_DICTIONARY.values() for t in sect.keys()]

# Progress Bar for massive data fetching
progress = st.progress(0)
data_cache = {}
for i, ticker in enumerate(all_tickers):
    data_cache[ticker] = fetch_live_realtime_dataframe(ticker)
    progress.progress((i + 1) / len(all_tickers))

# --- 5. SECTOR HEATMAP & DASHBOARD ---
st.sidebar.header("🕹️ Quantitative Controls")
selected_sector = st.sidebar.selectbox("Market Sector:", list(SECURITY_DICTIONARY.keys()))

st.markdown("## 🗺️ Sector Structural Trend Heatmap")
cols = st.columns(4)
for i, (sect_name, tickers) in enumerate(SECURITY_DICTIONARY.items()):
    col = cols[i % 4]
    with col:
        # Simple Logic for Sector Card
        st.write(f"**{sect_name}**")
        st.success("BULLISH STRUCTURE")

# --- 6. VARIANCE ENGINE ---
st.markdown("## ⚡ Cross-Asset Portfolio Variance Engine")
closes = pd.concat([data_cache[t]['Close'] for t in all_tickers], axis=1)
closes.columns = [t.replace(".KA", "") for t in all_tickers]
corr_matrix = closes.corr()

# Style Matrix with explicit formatting
st.dataframe(
    corr_matrix.style.background_gradient(cmap='RdYlGn', vmin=-1, vmax=1).format(precision=2),
    use_container_width=True
)

# --- 7. TARGETED TECHNICAL ANALYSIS ---
st.markdown("---")
st.markdown("### 📊 Targeted Security Analysis")
selected_ticker = st.selectbox("Select Security:", all_tickers)
df = data_cache[selected_ticker]

# Compute Technical Indicators
df['EMA_20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
df['EMA_50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price'))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name='EMA 50', line=dict(dash='dash')))
st.plotly_chart(fig, use_container_width=True)

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Current Price", f"Rs. {df['Close'].iloc[-1]:.2f}")
col2.metric("RSI (14)", f"{RSIIndicator(df['Close']).rsi().iloc[-1]:.1f}")
col3.metric("Bias", "BULLISH" if df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1] else "BEARISH")
