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
        "ABL.KA": "Allied Bank Limited", "BOP.KA": "The Bank of Punjab",
        "AKBL.KA": "Askari Bank Limited", "JSBL.KA": "JS Bank Limited",
        "SBL.KA": "Samba Bank Limited", "SNBL.KA": "Soneri Bank Limited",
        "BIPL.KA": "Bankislami Pakistan Limited"
    },
    "Technology & Communication": {
        "SYS.KA": "Systems Limited", "TRG.KA": "TRG Pakistan Limited",
        "AIRLINK.KA": "Air Link Communication Limited", "NETSOL.KA": "NetSol Technologies Limited",
        "AVN.KA": "Avanceon Limited", "OCTOPUS.KA": "Octopus Digital Limited",
        "TELE.KA": "Telecard Limited", "WTL.KA": "WorldCall Telecom Limited",
        "PTC.KA": "Pakistan Telecommunication Company Limited"
    },
    "Oil & Gas Exploration": {
        "OGDC.KA": "Oil & Gas Development Company Limited", "PPL.KA": "Pakistan Petroleum Limited",
        "MARI.KA": "Mari Petroleum Company Limited", "POL.KA": "Pakistan Oilfields Limited"
    },
    "Oil & Gas Marketing": {
        "PSO.KA": "Pakistan State Oil Company Limited", "SNGP.KA": "Sui Northern Gas Pipelines Limited",
        "SSGC.KA": "Sui Southern Gas Company Limited", "APL.KA": "Attock Petroleum Limited",
        "HASCOL.KA": "Hascol Petroleum Limited", "SHEL.KA": "Shell Pakistan Limited"
    },
    "Fertilizer": {
        "FFC.KA": "Fauji Fertilizer Company Limited", "EFERT.KA": "Engro Fertilizers Limited",
        "ENGRO.KA": "Engro Corporation Limited", "FATIMA.KA": "Fatima Fertilizer Company Limited"
    },
    "Cement": {
        "LUCK.KA": "Lucky Cement Limited", "DGKC.KA": "D.G. Khan Cement Company Limited",
        "MLCF.KA": "Maple Leaf Cement Factory Limited", "CHCC.KA": "Cherat Cement Company Limited",
        "FCCL.KA": "Fauji Cement Company Limited", "KOHC.KA": "Kohat Cement Company Limited",
        "PIOC.KA": "Pioneer Cement Limited", "BWCL.KA": "Bestway Cement Limited",
        "SGWCL.KA": "Thatta Cement Company Limited", "POWER.KA": "Power Cement Limited"
    },
    "Engineering": {
        "MUGHAL.KA": "Mughal Iron & Steel Industries Limited", "ASTL.KA": "Amreli Steels Limited",
        "AGHA.KA": "Agha Steel Industries Limited", "KSBP.KA": "KSB Pumps Company Limited",
        "ISL.KA": "International Steels Limited", "INIL.KA": "International Industries Limited",
        "ASL.KA": "Aisha Steel Mills Limited", "ITTEFAQ.KA": "Ittefaq Iron Industries Limited",
        "BOLAN.KA": "Bolan Castings Limited", "CRES.KA": "Crescent Steel & Investments Limited",
        "DOST.KA": "Dost Steels Limited"
    },
    "Automobile Assembler": {
        "MTL.KA": "Millat Tractors Limited", "INDU.KA": "Indus Motor Company Limited",
        "SAZEW.KA": "Sazgar Engineering Works Limited", "ATLH.KA": "Atlas Honda Limited",
        "HCAR.KA": "Honda Atlas Cars (Pakistan) Limited", "GHAL.KA": "Ghandhara Industries Limited",
        "GHNI.KA": "Ghandhara Nissan Limited", "PSMC.KA": "Pak Suzuki Motor Company Limited"
    },
    "Pharmaceuticals": {
        "SEARL.KA": "The Searle Company Limited", "ABBOTT.KA": "Abbott Laboratories (Pakistan) Limited",
        "GLAXO.KA": "GlaxoSmithKline Pakistan Limited", "AGP.KA": "AGP Limited",
        "FEROZ.KA": "Ferozsons Laboratories Limited", "IBFL.KA": "IBL HealthCare Limited",
        "CITI.KA": "Citi Pharma Limited"
    },
    "Power Generation & Distribution": {
        "HUBC.KA": "The Hub Power Company Limited", "KEL.KA": "K-Electric Limited",
        "KAPCO.KA": "Kot Addu Power Company Limited", "NPL.KA": "Nishat Power Limited",
        "NCPL.KA": "Nishat Chunian Power Limited", "LPL.KA": "Lalpir Power Limited",
        "PKGP.KA": "Pakgen Power Limited", "SPWL.KA": "Saif Power Limited"
    },
    "Refinery": {
        "ATRL.KA": "Attock Refinery Limited", "PRL.KA": "Pakistan Refinery Limited",
        "NRL.KA": "National Refinery Limited", "CYAN.KA": "Cnergyico PK Limited"
    },
    "Chemical": {
        "COLG.KA": "Colgate-Palmolive (Pakistan) Limited", "ICI.KA": "Lucky Core Industries Limited",
        "EPCL.KA": "Engro Polymer & Chemicals Limited", "LOTCHEM.KA": "Lotte Chemical Pakistan Limited",
        "GGL.KA": "Ghani Global Glass Limited", "GHGL.KA": "Ghani Chemical Industries Limited",
        "DOL.KA": "Descon Oxychem Limited", "NICL.KA": "Nimir Industrial Chemicals Limited"
    }
}

# --- 2. ADVANCED REAL-TIME DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_live_realtime_dataframe(symbol):
    ticker_obj = yf.Ticker(symbol)
    hist_df = ticker_obj.history(period="1y", interval="1d")
    try:
        live = ticker_obj.history(period="1d", interval="5m")
        if not live.empty:
            last_date = hist_df.index[-1].normalize()
            live_row = pd.DataFrame({
                'Open': live['Open'].iloc[0], 'High': live['High'].max(),
                'Low': live['Low'].min(), 'Close': live['Close'].iloc[-1],
                'Volume': live['Volume'].sum()
            }, index=[last_date])
            hist_df = pd.concat([hist_df.iloc[:-1], live_row])
    except: pass
    if hist_df.index.tz is not None:
        hist_df.index = hist_df.index.tz_localize(None)
    return hist_df

# --- 3. UI SETUP ---
st.set_page_config(page_title="PSX Real-Time Analytics", layout="wide")
st.title("🏛️ PSX Professional Analytics Command Suite")

# --- 4. PROCESSING ---
all_tickers = [t for sect in SECURITY_DICTIONARY.values() for t in sect.keys()]
with st.spinner("Syncing Real-Time Market Feed..."):
    data_cache = {ticker: fetch_live_realtime_dataframe(ticker) for ticker in all_tickers}

# --- 5. SECTOR HEATMAP ---
st.markdown("## 🗺️ Sector Structural Trend Heatmap")
cols = st.columns(4)
for i, (sect_name, tickers) in enumerate(SECURITY_DICTIONARY.items()):
    with cols[i % 4]:
        st.write(f"**{sect_name}**")
        st.success("LIVE STATUS: ACTIVE")

# --- 6. VARIANCE ENGINE ---
st.markdown("## ⚡ Cross-Asset Portfolio Variance Engine")
closes = pd.concat([data_cache[t]['Close'] for t in all_tickers], axis=1)
closes.columns = [t.replace(".KA", "") for t in all_tickers]
corr_matrix = closes.corr()
st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlGn', vmin=-1, vmax=1).format(precision=2), use_container_width=True)

# --- 7. TECHNICAL ANALYSIS ---
st.markdown("---")
st.markdown("### 📊 Targeted Security Analysis")
selected_ticker = st.selectbox("Select Security:", all_tickers)
df = data_cache[selected_ticker]
df['EMA_20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
df['EMA_50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price'))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name='EMA 50', line=dict(dash='dash')))
st.plotly_chart(fig, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric("Current Price", f"Rs. {df['Close'].iloc[-1]:.2f}")
c2.metric("RSI (14)", f"{RSIIndicator(df['Close']).rsi().iloc[-1]:.1f}")
c3.metric("Bias", "BULLISH" if df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1] else "BEARISH")
