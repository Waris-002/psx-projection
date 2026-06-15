import time
import yfinance as yf
import streamlit as st

# --- OPTIMIZED BATCH FETCHING ENGINE ---
@st.cache_data(ttl=3600)  # Extended TTL to reduce API load
def fetch_psx_market_data(all_tickers):
    """
    Uses yfinance Tickers() for batching and adds deliberate 
    throttling to bypass YFRateLimitError.
    """
    data_cache = {}
    # Batch the tickers into groups of 10 to stay under the radar
    chunk_size = 10
    for i in range(0, len(all_tickers), chunk_size):
        chunk = all_tickers[i:i + chunk_size]
        
        # Batch fetch using YF Tickers
        batch = yf.Tickers(" ".join(chunk))
        
        for symbol in chunk:
            try:
                # Use history with a longer timeout
                hist = batch.tickers[symbol].history(period="1y", interval="1d", timeout=10)
                if not hist.empty:
                    # Clean the index (tz-naive)
                    hist.index = hist.index.tz_localize(None)
                    data_cache[symbol] = hist
                time.sleep(1.5)  # Throttling: 1.5s delay per ticker
            except Exception as e:
                st.warning(f"Could not fetch {symbol}: {e}")
                
    return data_cache

# --- HOW TO IMPLEMENT IN YOUR APP ---
# Replace your existing loop with this:
all_tickers = [t for sect in SECURITY_DICTIONARY.values() for t in sect.keys()]

with st.spinner("Syncing global real-time market matrices (Throttled)..."):
    data_cache = fetch_psx_market_data(all_tickers)
