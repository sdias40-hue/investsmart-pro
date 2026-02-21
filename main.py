import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface Profissional (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Total Control", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Busca e Análise Blindadas (Resolve image_41549e.png)
@st.cache_data(ttl=20)
def buscar_v250(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        info = tk.info
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if h.empty: return None, None, 0, 0, 0, 5.60, False
        
        # Lógica Fundamentalista vs Cripto (Fim do erro image_4144be.jpg)
        p_j, dpa, div = 0, 0, 0
        if not is_c:
            lpa = info.get('forwardEps', 0)
            vpa = info.get('bookValue', 0)
            p_j = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            dpa = info.get('dividendRate', 0)
            div_raw = info.get('dividendYield', 0)
            div = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw
            
        return h, info, div, dpa, p_j, usd_brl, is_c
    except: return None, None, 0, 0, 0, 5.60, False

# --- MEMÓRIA E ESTADOS ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO CENTRAL ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk_tg
