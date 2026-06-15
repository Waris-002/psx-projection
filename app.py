import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import time

# --- 1. CONFIGURATION & DICTIONARY ---
# Full dictionary of PSX securities
SECURITY_DICTIONARY = {
    "Commercial Banks": {
        "UBL.KA": "United Bank Limited", "MEBL.KA": "Meezan Bank Limited",
        "MCB.KA": "MCB Bank Limited", "HBL.KA": "Habib Bank Limited",
        "BAHL.KA": "Bank AL Habib Limited", "BAFL.KA": "Bank Alfalah Limited"
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

# --- 2. ADVANCED DATA ENGINE WITH THROTTLING ---
@st.cache_data(ttl=3600)
def fetch_psx_market_data(all_tickers):
    """
    Fetches data with batching and throttling to avoid YFRateLimitError.
    """
    data_cache = {}
    chunk_size = 5 # Smaller chunk size to stay under Yahoo API radar
    for i in range(0, len(all_tickers), chunk_size):
        chunk = all_tickers[i:i + chunk_size]
        batch = yf.Tickers(" ".join(chunk))
        
        for symbol in chunk:
            try:
                hist = batch.tickers[symbol].history(period="1y", interval="1d", timeout=10)
                if not hist.empty:
                    # Fix: Standardize timezone to avoid comparison errors
                    if hist.index.tz is not None:
                        hist.index = hist.index.tz_localize(None)
                    data_cache[symbol] = hist
                time.sleep(1.0) # Throttling delay
            except Exception as e:
                continue
    return data_cache

# --- 3. UI SETUP ---
st.set_page_config(page_title="PSX Analytics Suite", layout="wide")
st.title("🏛️ PSX Real-Time Analytics Command Suite")

all_tickers = [t for sect in SECURITY_DICTIONARY.values() for t in sect.keys()]

# Fix: Use correct casing for spinner
with st.spinner("Syncing global real-time market matrices..."):
    data_cache = fetch_psx_market_data(all_tickers)

# --- 4. VARIANCE ENGINE ---
st.markdown("## ⚡ Cross-Asset Portfolio Variance Engine")
# Fix: Ensure all_tickers contains valid keys from cache
valid_tickers = [t for t in all_tickers if t in data_cache]
closes = pd.concat([data_cache[t]['Close'] for t in valid_tickers], axis=1)
closes.columns = [t.replace(".KA", "") for t in valid_tickers]
corr_matrix = closes.corr()

# Note: Ensure matplotlib is in requirements.txt to support background_gradient
st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlGn').format(precision=2), use_container_width=True)

# --- 5. TARGETED TECHNICAL ANALYSIS ---
st.markdown("---")
st.markdown("### 📊 Targeted Security Technical Analysis")
selected_ticker = st.selectbox("Select Security:", valid_tickers)

df = data_cache[selected_ticker]
# Fix: Ensure df is defined before usage
df['EMA_20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
df['EMA_50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price'))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name='EMA 50', line=dict(dash='dash')))
st.plotly_chart(fig, use_container_width=True)
