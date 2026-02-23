import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface (Layout Premium Recuperado)
st.set_page_config(page_title="Sandro Trader Cloud", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Análise Trader
@st.cache_data(ttl=60)
def analisar_v510(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        div_raw = info.get('dividendYield', 0) or info.get('yield', 0) or 0
        div_f = (div_raw * 100) if (div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_a": div_f, "setor": info.get('sector', 'Trader Assets')
        }

        # Especialidade Trader: Volatilidade (image_d69d3b.jpg)
        h['Vol'] = h['Close'].pct_change().std() * np.sqrt(252)
        d["vol_anual"] = h['Vol'].iloc[-1]
        
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        if lpa and vpa and not is_c and info.get('quoteType') == 'EQUITY':
            d["pj"] = np.sqrt(22.5 * lpa * vpa)
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["tem_fund"] = True
        else:
            d["pj"], d["roe"], d["tem_fund"] = 0, 0, False
        
        # Tendências (image_4c07e0.png)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA SANDRO ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_fixa' not in st.session_state: st.session_state.consulta_fixa = None

# --- SIDEBAR: GESTÃO (Limpeza de Dados) ---
with st.sidebar:
    st.title("🛡️ Central Sandro Pro")
    with st.form("form_v510", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").
