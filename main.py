import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. Interface Premium (Visual Limpo e Legível)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; }
    .trader-box { background-color: #121212; color: #00FF00; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #00FF00; font-size: 18px; font-weight: bold; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência (Cripto vs Ações)
@st.cache_data(ttl=60)
def analisar_ativo(t):
    try:
        t_up = t.upper().strip()
        # Identifica se é Cripto Principal
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP", "BNB"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        # Cálculo de Dividendos (Renda Mensal Real)
        div_hist = tk.actions['Dividends'].last('1y')
        pago_total_ano = div_hist.sum() if not div_hist.empty else 0
        renda_mensal_un = pago_total_ano / 12
        
        # Perfil de Volatilidade
        vol = h['Close'].pct_change().std() * np.sqrt(252)
        perfil = "🚀 DAY TRADE (Alta Volatilidade)" if vol > 0.45 else "📈 SWING TRADE (Estável)"
        
        return {
            "h": h, "ticker": t_up, "pa": h['Close'].iloc[-1], "is_c": is_c,
            "renda_m": renda_mensal_un, "perfil": perfil, 
            "dy": (pago_total_ano/h['Close'].iloc[-1]) if pago_total_ano > 0 else 0,
            "sup": h['Low'].tail(30).min(), "res": h['High'].tail(30).max()
        }
    except: return None

# --- SIDEBAR NEXUS ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    obj_renda = st.number_input("Meta Renda Mensal Desejada (R$):", value=1000.0)
    
    with st.form("nexus_form"):
        t_in = st.text_input("Ticker (VULC3, BTC, JEPQ34):").upper().strip()
        p_compra = st.number_input("Preço que Paguei:", min_value=0.0)
        qtd = st.number_input("Quantidade que tenho:", min_value=0)
        if st.form_submit_button("🚀 Analisar Ativo"):
            st.session_state.consulta = t_in

# --- PAINEL PRINCIPAL ---
if 'consulta' in st.session_state and st.session_state.consulta:
    d = analisar_ativo(st.session_state.consulta)
    if d:
        st.markdown(f"<h1>Análise de Inteligência: <span style='color:#007bff'>{
