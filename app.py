import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator, MACD

# --- INSTITUTIONAL STRUCTURAL DICTIONARIES & QUANT MATRICES (94 SECURITIES) ---
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

CAP_WEIGHT_UNITS = {
    "UBL.KA": 420.0, "MEBL.KA": 380.0, "MCB.KA": 310.0, "HBL.KA": 180.0, "BAHL.KA": 160.0, "BAFL.KA": 140.0, "NBP.KA": 150.0, "FABL.KA": 75.0, "ABL.KA": 110.0, "BOP.KA": 25.0, "AKBL.KA": 35.0, "JSBL.KA": 15.0, "SBL.KA": 12.0, "SNBL.KA": 18.0, "BIPL.KA": 22.0,
    "SYS.KA": 140.0, "TRG.KA": 45.0, "AIRLINK.KA": 35.0, "NETSOL.KA": 12.0, "AVN.KA": 15.0, "OCTOPUS.KA": 8.0, "TELE.KA": 4.0, "WTL.KA": 12.0, "PTC.KA": 28.0,
    "OGDC.KA": 620.0, "PPL.KA": 340.0, "MARI.KA": 490.0, "POL.KA": 150.0,
    "PSO.KA": 90.0, "SNGP.KA": 45.0, "SSGC.KA": 12.0, "APL.KA": 55.0, "HASCOL.KA": 8.0, "SHEL.KA": 22.0,
    "FFC.KA": 410.0, "EFERT.KA": 250.0, "ENGRO.KA": 280.0, "FATIMA.KA": 95.0,
    "LUCK.KA": 240.0, "DGKC.KA": 38.0, "MLCF.KA": 42.0, "CHCC.KA": 36.0, "FCCL.KA": 52.0, "KOHC.KA": 44.0, "PIOC.KA": 28.0, "BWCL.KA": 110.0, "SGWCL.KA": 8.0, "POWER.KA": 14.0,
    "MUGHAL.KA": 32.0, "ASTL.KA": 12.0, "AGHA.KA": 8.0, "KSBP.KA": 6.0, "ISL.KA": 45.0, "INIL.KA": 38.0, "ASL.KA": 11.0, "ITTEFAQ.KA": 5.0, "BOLAN.KA": 4.0, "CRES.KA": 9.0, "DOST.KA": 3.0,
    "MTL.KA": 95.0, "INDU.KA": 130.0, "SAZEW.KA": 62.0, "ATLH.KA": 48.0, "HCAR.KA": 22.0, "GHAL.KA": 8.0, "GHNI.KA": 6.0, "PSMC.KA": 45.0,
    "SEARL.KA": 35.0, "ABBOTT.KA": 75.0, "GLAXO.KA": 24.0, "AGP.KA": 28.0, "FEROZ.KA": 14.0, "IBFL.KA": 8.0, "CITI.KA": 12.0,
    "HUBC.KA": 320.0, "KEL.KA": 110.0, "KAPCO.KA": 32.0, "NPL.KA": 14.0, "NCPL.KA": 11.0, "LPL.KA": 12.0, "PKGP.KA": 10.0, "SPWL.KA": 9.0,
    "ATRL.KA": 110.0, "PRL.KA": 28.0, "NRL.KA": 38.0, "CYAN.KA": 15.0,
    "COLG.KA": 180.0, "ICI.KA": 120.0, "EPCL.KA": 45.0, "LOTCHEM.KA": 32.0, "GGL.KA": 7.0, "GHGL.KA": 14.0, "DOL.KA": 6.0, "NICL.KA": 24.0
}

TOTAL_ESTIMATED_PSX_CAP = 12500.0

def compute_technical_metrics(df):
    if df.empty or len(df) < 50:
        return None
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df['EMA_20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
    df['EMA_50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()
    df['RSI'] = RSIIndicator(close=df['Close'], window=14).rsi()
    
    macd_init = MACD(close=df['Close'], window_fast=12, window_slow=26, window_sign=9)
    df['MACD'] = macd_init.macd()
    df['MACD_Signal'] = macd_init.macd_signal()
    
    bb_init = BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BB_High'] = bb_init.bollinger_hband()
    df['BB_Low'] = bb_init.bollinger_lband()
    return df

def generate_multi_horizon_signal(df):
    if df is None or df.empty:
        return "DATA_ERROR", 0.0
        
    latest_row = df.iloc[-1]
    timeframe_horizons = [5, 10, 15, 30]
    bullish_votes = 0
    total_votes = 0
    
    is_ema_bullish = latest_row['EMA_20'] > latest_row['EMA_50'] if ('EMA_20' in latest_row and 'EMA_50' in latest_row) else False
    if is_ema_bullish:
        bullish_votes += 2
    total_votes += 2
        
    if 'RSI' in latest_row:
        if 40 <= latest_row['RSI'] <= 68:
            bullish_votes += 1.5
        elif latest_row['RSI'] < 40:
            bullish_votes += 0.5
    total_votes += 1.5
    
    for horizon in timeframe_horizons:
        if len(df) >= horizon:
            slope, _ = np.polyfit(np.arange(horizon), df['Close'].tail(horizon).values, 1)
            if slope > 0:
                bullish_votes += 1.0
            total_votes += 1.0
            
    probability = (bullish_votes / total_votes) * 100
    
    if is_ema_bullish and probability >= 65.0:
        if 'RSI' in latest_row and latest_row['RSI'] > 74:
            action = "HOLD (Overextended Momentum)"
            probability = min(probability, 75.0)
        else:
            action = "STRONG BUY / ACCUMULATE"
    elif is_ema_bullish and probability >= 45.0:
        action = "HOLD / ACCUMULATE ON DIPS"
    elif not is_ema_bullish and probability >= 40.0:
        action = "SPECULATIVE BUY (Counter-Trend Reversal)"
    else:
        action = "LIQUIDATE / AVOID"
        if probability > 40: 
            probability = 70.0
            
    return action, round(probability, 1)

st.set_page_config(page_title="PSX Capital Analytics Command Suite", layout="wide")
st.title("🏛️ PSX Capital Analytics Command Suite")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ Quantitative Controls")
sector_keys = list(SECURITY_DICTIONARY.keys())
selected_sector = st.sidebar.selectbox("Target Core Market Sector:", sector_keys)
run_sector_analysis = st.sidebar.checkbox("Compute Value-Weighted Composite Sector Index", value=True)

ticker_mapping = SECURITY_DICTIONARY[selected_sector]
formatted_company_options = [f"{ticker} | {name}" for ticker, name in ticker_mapping.items()]

if run_sector_analysis:
    selected_company_formatted = st.sidebar.selectbox("Target Corporate Security Focus:", ["Locked - Composite System Engaged"], disabled=True)
else:
    selected_company_formatted = st.sidebar.selectbox("Target Corporate Security Focus:", formatted_company_options, disabled=False)

forecast_days = st.sidebar.slider("Interactive Plot Display Forecast Path (Days):", min_value=5, max_value=30, value=15)

# --- GLOBAL ENGINE DATA PRE-CALCULATION ---
@st.cache_data(ttl=120)
def compute_complete_market_matrix(days_span):
    diagnostics = {}
    all_companies_flat_list = []
    
    for sect in sector_keys:
        companies = SECURITY_DICTIONARY[sect]
        bullish_count, total_valid = 0, 0
        sector_cap_accumulator = 0.0
        total_volume_pkr_accumulator = 0.0
        
        for ticker in companies.keys():
            cap_val = CAP_WEIGHT_UNITS.get(ticker, 5.0)
            sector_cap_accumulator += cap_val
            try:
                t_obj = yf.Ticker(ticker)
                hist = t_obj.history(period="1y") 
                if not hist.empty and len(hist) >= days_span:
                    recent_window = hist.tail(days_span)
                    traded_value_pkr = (recent_window['Close'] * recent_window['Volume']).sum()
                    total_volume_pkr_accumulator += traded_value_pkr
                    
                    comp_metrics = compute_technical_metrics(hist)
                    if comp_metrics is not None:
                        latest_row = comp_metrics.iloc[-1]
                        _, tracking_prob = generate_multi_horizon_signal(comp_metrics)
                        
                        slope_current, _ = np.polyfit(np.arange(days_span), comp_metrics['Close'].tail(days_span).values, 1)
                        target_price_projection = latest_row['Close'] + (slope_current * days_span)
                        proj_display_string = f"🟢 Rs. {target_price_projection:.2f}" if slope_current >= 0 else f"🔴 Rs. {target_price_projection:.2f}"
                        
                        all_companies_flat_list.append({
                            "Ticker Symbol": ticker.replace(".KA",""),
                            "Company Name": companies[ticker],
                            "Sector": sect,
                            "Price (PKR)": round(latest_row['Close'], 2),
                            "RSI (14)": round(latest_row['RSI'], 2),
                            "Score Value": tracking_prob,
                            "Integrated Score": "🟢 BULLISH" if tracking_prob >= 55.0 else "🔴 BEARISH/RISK",
                            f"{days_span}-Day Projection": proj_display_string,
                            "_volume_raw": traded_value_pkr
                        })
                        
                        if len(hist) >= 50:
                            ema20 = comp_metrics['EMA_20'].iloc[-1]
                            ema50 = comp_metrics['EMA_50'].iloc[-1]
                            if ema20 > ema50: bullish_count += 1
                        else:
                            if hist['Close'].iloc[-1] > hist['Close'].iloc[-max(5, days_span)]: bullish_count += 1
                    total_valid += 1
            except: 
                pass
            
        cap_pct_of_psx = (sector_cap_accumulator / TOTAL_ESTIMATED_PSX_CAP) * 100
        bias_pct = (bullish_count / total_valid) * 100 if total_valid > 0 else 0.0
        bias = "BULLISH" if bias_pct >= 40.0 else "BEARISH"
        
        diagnostics[sect] = {
            "bias": bias,
            "bias_score": round(bias_pct, 1),
            "cap_pct": round(cap_pct_of_psx, 2),
            "volume_pkr": total_volume_pkr_accumulator
        }
    return diagnostics, all_companies_flat_list

with st.spinner("Processing structural matrix timeline across all 94 securities..."):
    heatmap_stats, complete_companies_pool = compute_complete_market_matrix(forecast_days)

# --- TOP SUGGESTIONS ALPHA ENGINE (DISPLAYED AT TOP) ---
st.markdown("## ⚡ Alpha Allocation Dashboard (Top High-Conviction Plays)")

# Alpha ranking math: Sort sectors by trend health percentage, using volume to break ties
sorted_alpha_sectors = sorted(sector_keys, key=lambda s: (heatmap_stats.get(s, {}).get("bias_score", 0.0), heatmap_stats.get(s, {}).get("volume_pkr", 0.0)), reverse=True)
top_3_sectors = sorted_alpha_sectors[:3]

suggested_sectors_data = []
for idx, s_name in enumerate(top_3_sectors):
    s_stats = heatmap_stats[s_name]
    vol_m_b = f"Rs. {s_stats['volume_pkr'] / 1e9:.2f}B" if s_stats['volume_pkr'] >= 1e9 else f"Rs. {s_stats['volume_pkr'] / 1e6:.1f}M"
    suggested_sectors_data.append({
        "Rank Allocation": f"🏅 Top Choice {idx+1}",
        "Target Market Sector": s_name,
        "Structural Trend Health": f"🟢 {s_stats['bias_score']}% Bullish Confluence",
        "Total Horizon Traded Liquidity": vol_m_b,
        "Sector Weight Index": f"{s_stats['cap_pct']}%"
    })

top_sectors_df = pd.DataFrame(suggested_sectors_data)

alpha_col1, alpha_col2 = st.columns([4, 5])

with alpha_col1:
    st.markdown("### 🏆 Top 3 Sector Allocations")
    st.dataframe(top_sectors_df, use_container_width=True, hide_index=True)

with alpha_col2:
    st.markdown("### 🎯 Top 5 Highest-Conviction Alpha Companies")
    # Filter the giant pool for firms belonging ONLY to the top 3 sectors, then sort by highest tracking score value
    pool_df = pd.DataFrame(complete_companies_pool)
    if not pool_df.empty:
        filtered_top_firms = pool_df[pool_df['Sector'].isin(top_3_sectors)]
        filtered_top_firms = filtered_top_firms.sort_values(by="Score Value", ascending=False).head(5)
        
        display_top_firms = filtered_top_firms[["Ticker Symbol", "Company Name", "Sector", "Price (PKR)", "Integrated Score", f"{forecast_days}-Day Projection"]]
        
        def highlight_alpha_cells(val):
            if "🟢" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            elif "🔴" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            return ''
            
        st.dataframe(
            display_top_firms.style.map(highlight_alpha_cells, subset=['Integrated Score', f"{forecast_days}-Day Projection"]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Insufficient timeline tracking volume array to compile macro asset lists.")

st.markdown("---")

# --- SECTOR HEATMAP ENGINE ---
st.markdown("### 🗺️ Systemic Sector Structural Trend Heatmap")
st.markdown(f"*Dynamic analytics sorted from **maximum to minimum traded volume** for exactly the last **{forecast_days} trading days**.*")

sorted_heatmap_keys = sorted(sector_keys, key=lambda s: heatmap_stats.get(s, {}).get("volume_pkr", 0.0), reverse=True)

for row_idx in range(0, len(sorted_heatmap_keys), 4):
    row_sectors = sorted_heatmap_keys[row_idx:row_idx + 4]
    columns_track = st.columns(4)
    
    for i, sect in enumerate(row_sectors):
        col_slot = columns_track[i]
        data_bundle = heatmap_stats.get(sect, {"bias": "BEARISH", "cap_pct": 1.5, "volume_pkr": 0.0})
        volume_display = f"{data_bundle['volume_pkr'] / 1e6:.1f}M" if data_bundle['volume_pkr'] < 1e9 else f"{data_bundle['volume_pkr'] / 1e9:.2f}B"
        
        if data_bundle["bias"] == "BULLISH":
            col_slot.markdown(f"""
            <div style="background-color:#d4edda; border-left:6px solid #28a745; padding:14px; border-radius:4px; min-height:140px; margin-bottom:20px; display:flex; flex-direction:column; justify-content:space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div>
                    <b style="color:#155724; font-size:14px; line-height:1.2; display:block; margin-bottom:6px;">{sect}</b>
                    <span style="color:#28a745; font-size:11px; font-weight:bold; letter-spacing:0.5px;">🟢 BULLISH TREND STRUCTURE</span>
                </div>
                <div style="border-top: 1px solid rgba(40,167,69,0.15); padding-top:6px; margin-top:6px; color:#555555; font-size:11px; font-family:-apple-system,Sans-Serif; line-height:1.3;">
                    Sector Weight: <b>{data_bundle['cap_pct']}%</b><br>
                    Total Volume ({forecast_days}D): <b>Rs. {volume_display}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            col_slot.markdown(f"""
            <div style="background-color:#f8d7da; border-left:6px solid #dc3545; padding:14px; border-radius:4px; min-height:140px; margin-bottom:20px; display:flex; flex-direction:column; justify-content:space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div>
                    <b style="color:#721c24; font-size:14px; line-height:1.2; display:block; margin-bottom:6px;">{sect}</b>
                    <span style="color:#dc3545; font-size:11px; font-weight:bold; letter-spacing:0.5px;">🔴 CONSOLIDATION / RISK</span>
                </div>
                <div style="border-top: 1px solid rgba(220,53,69,0.15); padding-top:6px; margin-top:6px; color:#555555; font-size:11px; font-family:-apple-system,Sans-Serif; line-height:1.3;">
                    Sector Weight: <b>{data_bundle['cap_pct']}%</b><br>
                    Total Volume ({forecast_days}D): <b>Rs. {volume_display}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# --- CORE QUANT ENGINE ---
if st.sidebar.button("Execute Quantitative Processing Engine"):
    
    if run_sector_analysis:
        st.subheader(f"📊 Value-Weighted Structural Index Matrix: {selected_sector}")
        target_tickers = list(ticker_mapping.keys())
        
        matrix_dataframe_list, individual_company_records = [], []
        weight_sum_tracker = 0.0
        progress_bar = st.progress(0)
        
        for idx, ticker in enumerate(target_tickers):
            try:
                t_obj = yf.Ticker(ticker)
                raw_df = t_obj.history(period="1y")
                if not raw_df.empty and len(raw_df) > 35:
                    weight_factor = CAP_WEIGHT_UNITS.get(ticker, 10.0)
                    normalized_indexed_series = (raw_df['Close'] / raw_df['Close'].iloc[0]) * 100
                    weighted_vector_series = normalized_indexed_series * weight_factor
                    
                    matrix_dataframe_list.append(weighted_vector_series.to_frame(name=ticker))
                    weight_sum_tracker += weight_factor
                    
                    company_recent_window = raw_df.tail(forecast_days)
                    company_traded_val_pkr = (company_recent_window['Close'] * company_recent_window['Volume']).sum()
                    
                    comp_metrics = compute_technical_metrics(raw_df)
                    if comp_metrics is not None:
                        latest_row = comp_metrics.iloc[-1]
                        _, tracking_prob = generate_multi_horizon_signal(comp_metrics)
                        
                        slope_current, _ = np.polyfit(np.arange(forecast_days), comp_metrics['Close'].tail(forecast_days).values, 1)
                        target_price_projection = latest_row['Close'] + (slope_current * forecast_days)
                        proj_display_string = f"🟢 Rs. {target_price_projection:.2f}" if slope_current >= 0 else f"🔴 Rs. {target_price_projection:.2f}"
                        
                        individual_company_records.append({
                            "Ticker Symbol": ticker.replace(".KA",""),
                            "Corporate Legal Name": ticker_mapping[ticker],
                            "Last Traded Price (PKR)": round(latest_row['Close'], 2),
                            "Momentum Index (RSI)": round(latest_row['RSI'], 2),
                            "Trend Alignment Floor": "Above Support" if latest_row['EMA_20'] > latest_row['EMA_50'] else "Below Base",
                            "Integrated Strategy Score": "🟢 BULLISH" if tracking_prob >= 55.0 else "🔴 BEARISH/RISK",
                            f"{forecast_days}-Day Projected Vector Price": proj_display_string,
                            "_sort_vol": company_traded_val_pkr
                        })
            except: 
                pass
            progress_bar.progress((idx + 1) / len(target_tickers))
            
        if matrix_dataframe_list and weight_sum_tracker > 0:
            combined_weights_df = pd.concat(matrix_dataframe_list, axis=1).dropna(how='all')
            sector_index_series = combined_weights_df.sum(axis=1) / weight_sum_tracker
            
            composite_df = sector_index_series.to_frame(name='Close')
            composite_df['Open'] = composite_df['Close']
            composite_df['High'] = composite_df['Close']
            composite_df['Low'] = composite_df['Close']
            composite_df['Volume'] = 100000
            
            df = compute_technical_metrics(composite_df)
            if df is not None:
                slope, _ = np.polyfit(np.arange(forecast_days), df['Close'].tail(forecast_days).values, 1)
                future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='B')
                projection_prices = [df['Close'].iloc[-1] + (slope * i) for i in range(1, forecast_days + 1)]
                
                view_df = df.tail(60)
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(x=view_df.index, y=view_df['Close'], name='Sector Index Weight Price', line=dict(color='#4b0082', width=3), hovertemplate='Date: %{x}<br>Weighted Sector Price: %{y:.2f}'))
                fig.add_trace(go.Scatter(x=view_df.index, y=view_df['EMA_20'], name='EMA 20 Support', line=dict(color='#ff7f0e', dash='dash')))
                fig.add_trace(go.Scatter(x=view_df.index, y=view_df['EMA_50'], name='EMA 50 Baseline', line=dict(color='#2ca02c', dash='dash')))
                
                p_dates = [df.index[-1]] + list(future_dates)
                p_prices = [df['Close'].iloc[-1]] + projection_prices
                fig.add_trace(go.Scatter(x=p_dates, y=p_prices, name=f'{forecast_days}-Day Chart Forecast', line=dict(color='#d62728', width=3, dash='dot'), marker=dict(size=6)))
                
                fig.update_layout(title=f"Interactive Capital-Weighted Index Model ({forecast_days}-Day Horizon): {selected_sector}", hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
                
                latest = df.iloc[-1]
                action_recommendation, action_probability = generate_multi_horizon_signal(df)
                
                st.markdown(f"### 🎯 Confluence Action Signals Allocation Engine (Cross-Horizon Analysis Enabled)")
                col1, col2, col3 = st.columns(3)
                col1.metric("Weighted Sector Index Baseline", f"{latest['Close']:.2f}")
                col2.metric("Integrated Strategic Profile Call", action_recommendation)
                col3.metric("Multi-Horizon Probability Score", f"{action_probability}% Buy Profile")
            
            st.markdown("---")
            st.markdown(f"### 📋 Underlying Sector Component Health Tracker: {selected_sector} *(Sorted by Volatility/Liquidity)*")
            if individual_company_records:
                rec_df = pd.DataFrame(individual_company_records)
                rec_df = rec_df.sort_values(by="_sort_vol", ascending=False).drop(columns=["_sort_vol"])
                
                def highlight_matrix_cells(val):
                    if "🟢" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                    elif "🔴" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                    return ''
                    
                st.dataframe(
                    rec_df.style.map(highlight_matrix_cells, subset=['Integrated Strategy Score', f"{forecast_days}-Day Projected Vector Price"]), 
                    use_container_width=True, 
                    hide_index=True
                )
        else:
            st.error("Failed executing sector index calculations due to API timeout.")

    else:
        target_ticker_symbol = selected_company_formatted.split(" | ")[0].strip()
        corporate_full_name = selected_company_formatted.split(" | ")[1].strip()
        
        st.subheader(f"🔍 Security Micro Evaluation Profile")
        
        with st.spinner("Computing corporate pricing indicators..."):
            t_obj = yf.Ticker(target_ticker_symbol)
            raw_df = t_obj.history(period="1y")
            df = compute_technical_metrics(raw_df)
            
            if df is not None and not df.empty:
                slope, _ = np.polyfit(np.arange(forecast_days), df['Close'].tail(forecast_days).values, 1)
                future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq='B')
                projection_prices = [df['Close'].iloc[-1] + (slope * i) for i in range(1, forecast_days + 1)]
                
                view_df = df.tail(60)
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(x=view_df.index, y=view_df['Close'], name=f"{target_ticker_symbol.replace('.KA','')}", line=dict(color='#1f77b4', width=3), hovertemplate='Date: %{x}<br>Company Price: %{y:.2f} PKR'))
                fig.add_trace(go.Scatter(x=view_df.index, y=view_df['EMA_20'], name='EMA 20 Velocity', line=dict(color='#ff7f0e', dash='dash')))
                fig.add_trace(go.Scatter(x=view_df.index, y=view_df['EMA_50'], name='EMA 50 Baseline', line=dict(color='#2ca02c', dash='dash')))
                
                p_dates = [df.index[-1]] + list(future_dates)
                p_prices = [df['Close'].iloc[-1]] + projection_prices
                fig.add_trace(go.Scatter(x=p_dates, y=p_prices, name=f'{forecast_days}-Day Chart Forecast', line=dict(color='#d62728', width=3, dash='dot'), marker=dict(size=6)))
                
                fig.update_layout(title=f"Interactive Price History & {forecast_days}-Day Future Projection: {corporate_full_name}", hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
                
                latest = df.iloc[-1]
                action_recommendation, action_probability = generate_multi_horizon_signal(df)
                
                st.markdown(f"### 🎯 Security Strategic Position Allocation Signals (Cross-Horizon Analysis Enabled)")
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Current Market Price Close", f"{latest['Close']:.2f} PKR")
                m_col2.metric("Integrated Strategic Profile Call", action_recommendation)
                m_col3.metric("Multi-Horizon Probability Score", f"{action_probability}% Buy Profile")
