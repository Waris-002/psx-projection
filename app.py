import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator

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
    return df

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

# --- GLOBAL ENGINE DATA PRE-CALCULATION WITH RETURNS SERIES ---
@st.cache_data(ttl=120)
def compute_complete_market_matrix(days_span):
    diagnostics = {}
    all_companies_flat_list = []
    returns_master_dict = {}
    
    for sect in sector_keys:
        companies = SECURITY_DICTIONARY[sect]
        bullish_count, total_valid = 0, 0
        sector_cap_accumulator = 0.0
        total_volume_pkr_accumulator = 0.0
        
        for ticker in companies.keys():
            sector_cap_accumulator += CAP_WEIGHT_UNITS.get(ticker, 5.0)
            try:
                t_obj = yf.Ticker(ticker)
                hist = t_obj.history(period="1y") 
                if not hist.empty and len(hist) >= 60:
                    recent_window = hist.tail(days_span)
                    traded_value_pkr = (recent_window['Close'] * recent_window['Volume']).sum()
                    total_volume_pkr_accumulator += traded_value_pkr
                    
                    pct_returns = hist['Close'].pct_change().dropna()
                    symbol_short = ticker.replace(".KA","")
                    returns_master_dict[symbol_short] = pct_returns.tail(60)
                    
                    comp_metrics = compute_technical_metrics(hist)
                    if comp_metrics is not None:
                        latest_row = comp_metrics.iloc[-1]
                        
                        ema20 = latest_row['EMA_20']
                        ema50 = latest_row['EMA_50']
                        tracking_prob = 75.0 if ema20 > ema50 else 35.0
                        
                        slope_current, _ = np.polyfit(np.arange(days_span), comp_metrics['Close'].tail(days_span).values, 1)
                        target_price_projection = latest_row['Close'] + (slope_current * days_span)
                        proj_display_string = f"🟢 Rs. {target_price_projection:.2f}" if slope_current >= 0 else f"🔴 Rs. {target_price_projection:.2f}"
                        
                        all_companies_flat_list.append({
                            "Ticker Symbol": symbol_short,
                            "Company Name": companies[ticker],
                            "Sector": sect,
                            "Price (PKR)": round(latest_row['Close'], 2),
                            "Score Value": tracking_prob,
                            "Integrated Score": "🟢 BULLISH" if tracking_prob >= 55.0 else "🔴 BEARISH/RISK",
                            f"{days_span}-Day Projection": proj_display_string,
                            "_volume_raw": traded_value_pkr
                        })
                        if ema20 > ema50: bullish_count += 1
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
    return diagnostics, all_companies_flat_list, pd.DataFrame(returns_master_dict)

with st.spinner("Processing structural trend tracking matrix..."):
    heatmap_stats, complete_companies_pool, master_returns_df = compute_complete_market_matrix(forecast_days)

# --- ⚡ CROSS-ASSET PORTFOLIO VARIANCE HEDGE ENGINE ---
st.markdown("## ⚡ Cross-Asset Portfolio Variance Engine (Dynamic Net-Off)")

pool_df = pd.DataFrame(complete_companies_pool)

if not pool_df.empty and not master_returns_df.empty:
    top_gainers_pool = pool_df[pool_df["Integrated Score"] == "🟢 BULLISH"].sort_values(by="Score Value", ascending=False).head(3)
    
    if len(top_gainers_pool) >= 3:
        gainer_tickers = top_gainers_pool["Ticker Symbol"].tolist()
        global_corr_matrix = master_returns_df.corr()
        
        avg_market_correlations = global_corr_matrix[gainer_tickers].mean(axis=1).dropna()
        sorted_hedges = avg_market_correlations.sort_values(ascending=True)
        
        hedge_records = []
        added_hedges = set(gainer_tickers)
        
        for tik, corr_val in sorted_hedges.items():
            if len(hedge_records) >= 3:
                break
            if tik in added_hedges:
                continue
            match_row = pool_df[pool_df["Ticker Symbol"] == tik]
            if not match_row.empty:
                hedge_records.append(match_row.iloc[0])
                added_hedges.add(tik)
                
        top_hedges_pool = pd.DataFrame(hedge_records)
        
        top_gainers_pool["Allocation Mode"] = "🚀 ALPHA LONG"
        top_hedges_pool["Allocation Mode"] = "🛡️ HEDGE SHORT-NET"
        
        combined_portfolio_df = pd.concat([top_gainers_pool, top_hedges_pool]).copy()
        portfolio_tickers = combined_portfolio_df["Ticker Symbol"].tolist()
        
        lead_alpha = gainer_tickers[0]
        coefficients = [round(global_corr_matrix[lead_alpha].get(t, 1.0), 2) for t in portfolio_tickers]
        corr_col_title = f"Correlation vs {lead_alpha}"
        combined_portfolio_df[corr_col_title] = coefficients
        
        sub_matrix = global_corr_matrix[portfolio_tickers].loc[portfolio_tickers]
        upper_tri_elements = sub_matrix.values[np.triu_indices_from(sub_matrix, k=1)]
        avg_portfolio_covariance = np.mean(upper_tri_elements) if len(upper_tri_elements) > 0 else 0.0
        
        net_off_efficiency = max(0.0, min(100.0, (1.0 - avg_portfolio_covariance) * 50.0))
        
        alpha_col1, alpha_col2 = st.columns([1, 1])
        
        with alpha_col1:
            st.markdown("### 🎯 Automatically Constructed Balanced Portfolio Matrix")
            display_cols = ["Allocation Mode", "Ticker Symbol", "Company Name", "Sector", "Price (PKR)", corr_col_title]
            
            def highlight_portfolio_style(val):
                if "🚀 ALPHA LONG" in str(val): return 'background-color: #e8f4fd; color: #004085; font-weight: bold;'
                if "🛡️ HEDGE SHORT-NET" in str(val): return 'background-color: #fef9e7; color: #856404; font-weight: bold;'
                try:
                    if float(val) < 0.10: return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                except ValueError: pass
                return ''
                
            st.dataframe(
                combined_portfolio_df[display_cols].style.map(highlight_portfolio_style),
                use_container_width=True, hide_index=True
            )
            
            st.info(f"🔄 **Hedging Engine Analysis: Multi-Asset Variance Strategy achieved {net_off_efficiency:.1f}% Effective Systematic Risk Net-Off.**")
            
        with alpha_col2:
            st.markdown("### 📊 Internal Portfolio Covariance Structure Matrix")
            
            # Pure CSS Heatmap Engine avoiding external library requirements
            def style_covariance_matrix(val):
                try:
                    v = float(val)
                    if v >= 0.70: return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                    elif 0.30 <= v < 0.70: return 'background-color: #fff3cd; color: #856404;'
                    elif -0.10 < v < 0.30: return 'background-color: #f8f9fa; color: #212529;'
                    else: return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                except ValueError: return ''

            st.dataframe(
                sub_matrix.style.map(style_covariance_matrix).format(precision=2),
                use_container_width=True
            )
    else:
        st.info("System currently processing sector configurations...")
else:
    st.info("Insufficient parallel pricing history to run global correlation analysis.")

st.markdown("---")

# --- SECTOR HEATMAP ENGINE ---
st.markdown("### 🗺️ Systemic Sector Structural Trend Heatmap")
sorted_heatmap_keys = sorted(sector_keys, key=lambda s: heatmap_stats.get(s, {}).get("volume_pkr", 0.0), reverse=True)

for row_idx in range(0, len(sorted_heatmap_keys), 4):
    row_sectors = sorted_heatmap_keys[row_idx:row_idx + 4]
    columns_track = st.columns(4)
    for i, sect in enumerate(row_sectors):
        col_slot = columns_track[i]
        data_bundle = heatmap_stats.get(sect, {"bias": "BEARISH", "cap_pct": 1.5, "volume_pkr": 0.0})
        volume_display = f"{data_bundle['volume_pkr'] / 1e6:.1f}M" if data_bundle['volume_pkr'] < 1e9 else f"{data_bundle['volume_pkr'] / 1e9:.2f}B"
        if data_bundle["bias"] == "BULLISH":
            col_slot.markdown(f"""<div style="background-color:#d4edda; border-left:6px solid #28a745; padding:14px; border-radius:4px; min-height:140px; margin-bottom:20px;"><b style="color:#155724; font-size:14px;">{sect}</b><br><span style="color:#28a745; font-size:11px; font-weight:bold;">🟢 BULLISH STRUCTURE</span><br><small style="color:#555;">Weight: {data_bundle['cap_pct']}%<br>Vol: Rs. {volume_display}</small></div>""", unsafe_allow_html=True)
        else:
            col_slot.markdown(f"""<div style="background-color:#f8d7da; border-left:6px solid #dc3545; padding:14px; border-radius:4px; min-height:140px; margin-bottom:20px;"><b style="color:#721c24; font-size:14px;">{sect}</b><br><span style="color:#dc3545; font-size:11px; font-weight:bold;">🔴 RISK/CONSOLIDATION</span><br><small style="color:#555;">Weight: {data_bundle['cap_pct']}%<br>Vol: Rs. {volume_display}</small></div>""", unsafe_allow_html=True)

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
                    matrix_dataframe_list.append((normalized_indexed_series * weight_factor).to_frame(name=ticker))
                    weight_sum_tracker += weight_factor
                    
                    company_recent_window = raw_df.tail(forecast_days)
                    company_traded_val_pkr = (company_recent_window['Close'] * company_recent_window['Volume']).sum()
                    comp_metrics = compute_technical_metrics(raw_df)
                    if comp_metrics is not None:
                        latest_row = comp_metrics.iloc[-1]
                        
                        ema20 = latest_row['EMA_20']
                        ema50 = latest_row['EMA_50']
                        tracking_prob = 75.0 if ema20 > ema50 else 35.0
                        
                        slope_current, _ = np.polyfit(np.arange(forecast_days), comp_metrics['Close'].tail(forecast_days).values, 1)
                        proj_display_string = f"🟢 Rs. {latest_row['Close'] + (slope_current * forecast_days):.2f}" if slope_current >= 0 else f"🔴 Rs. {latest_row['Close'] + (latest_row['Close'] + (slope_current * forecast_days)):.2f}"
                        
                        individual_company_records.append({
                            "Ticker Symbol": ticker.replace(".KA",""),
                            "Corporate Legal Name": ticker_mapping[ticker],
                            "Last Traded Price (PKR)": round(latest_row['Close'], 2),
                            "Momentum Index (RSI)": round(latest_row['RSI'], 2),
                            "Trend Alignment Floor": "Above Support" if ema20 > ema50 else "Below Base",
                            "Integrated Strategy Score": "🟢 BULLISH" if tracking_prob >= 55.0 else "🔴 BEARISH/RISK",
                            f"{forecast_days}-Day Projected Vector Price": proj_display_string,
                            "_sort_vol": company_traded_val_pkr
                        })
            except: pass
            progress_bar.progress((idx + 1) / len(target_tickers))
            
        if matrix_dataframe_list and weight_sum_tracker > 0:
            combined_weights_df = pd.concat(matrix_dataframe_list, axis=1).dropna(how='all')
            composite_df = (combined_weights_df.sum(axis=1) / weight_sum_tracker).to_frame(name='Close')
            composite_df['Open'] = composite_df['Close']
            composite_df['High'] = composite_df['Close']
            composite_df['Low'] = composite_df['Close']
            composite_df['Volume'] = 100000
            
            df = compute_technical_metrics(composite_df)
            if df is not None:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.tail(60).index, y=df.tail(60)['Close'], name='Sector Index Price', line=dict(color='#4b0082', width=3)))
                fig.add_trace(go.Scatter(x=df.tail(60).index, y=df.tail(60)['EMA_20'], name='EMA 20 Support', line=dict(color='#ff7f0e', dash='dash')))
                fig.add_trace(go.Scatter(x=df.tail(60).index, y=df.tail(60)['EMA_50'], name='EMA 50 Baseline', line=dict(color='#2ca02c', dash='dash')))
                st.plotly_chart(fig, use_container_width=True)
                
                latest_idx_row = df.iloc[-1]
                action_rec = "STRONG BUY" if latest_idx_row['EMA_20'] > latest_idx_row['EMA_50'] else "LIQUIDATE / AVOID"
                action_prob = 75.0 if latest_idx_row['EMA_20'] > latest_idx_row['EMA_50'] else "LIQUIDATE / AVOID"
                
                st.markdown(f"### 🎯 Confluence Action Signals Allocation Engine")
                col1, col2, col3 = st.columns(3)
                col1.metric("Index Baseline", f"{latest_idx_row['Close']:.2f}")
                col2.metric("Strategic Call", action_rec)
                col3.metric("Probability Score", f"{action_prob}% Buy Profile")
            
            st.markdown("---")
            if individual_company_records:
                rec_df = pd.DataFrame(individual_company_records).sort_values(by="_sort_vol", ascending=False).drop(columns=["_sort_vol"])
                proj_col_name = f"{forecast_days}-Day Projected Vector Price"
                
                def highlight_matrix_cells(val):
                    if "🟢" in str(val): return 'background-color: #d4edda; font-weight: bold; color: #155724;'
                    return ''
                
                st.dataframe(
                    rec_df.style.map(highlight_matrix_cells, subset=['Integrated Strategy Score', proj_col_name]), 
                    use_container_width=True, 
                    hide_index=True
                )
