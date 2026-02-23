import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (image_d4d43a.png)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência Sincronizado (Correção de Divergência image_e439b3.png)
@st.cache_data(ttl=60)
def analisar_v620(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        total_pago_12m = div_hist.sum()
        
        # Periodicidade (image_e4397d.png)
        freq = "Mensal" if len(div_hist) >= 10 else ("Semestral/Anual" if len(div_hist) >= 1 else "N/A")

        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_12m": total_pago_12m, "freq": freq, "div_hist": div_hist,
            "setor": info.get('sector', 'N/A'), "roe": (info.get('returnOnEquity', 0) or 0) * 100
        }

        # Graham (image_e20607.png)
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Canais Técnicos (image_4c07e0.png)
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA (Proteção contra KeyError image_e4a9dd.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO NEXUS ( image_4c1edf.png) ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    obj_renda = st.number_input("Meta Renda Mensal (R$):", min_value=0.0, value=1000.0)
    
    with st.form("form_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        is_cripto = t_in in ["BTC", "ETH", "SOL", "XRP"]
        
        if is_cripto:
            p_compra = st.number_input("Preço Entrada (US$):", min_value=0.0, format="%.4f")
            val_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            qtd = 0
        else:
            p_compra = st.number_input("Preço Compra (R$):", min_value=0.0)
            qtd = st.number_input("Quantidade:", min_value=0, step=1)
            
        p_alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        if st.form_submit
