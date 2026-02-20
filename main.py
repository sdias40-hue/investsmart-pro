import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Layout High Clarity (Fundo Branco - image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 12px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-weight: 800; }
    .stInfo { background-color: #ffffff !important; border-left: 5px solid #007bff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte (Correção de Causa Raiz)
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v90(t):
    try:
        # Identificação robusta de Cripto/Global para evitar erro de preço (image_e1717f.jpg)
        globals = ["BTC", "XRP", "ETH", "SOL", "OHI", "AAPL"]
        search = f"{t.upper()}-USD" if t.upper() in globals and "-" not in t else (t if ".SA" in t or "-" in t else f"{t}.SA")
        ticker = yf.Ticker(search)
        # Puxa dólar real para conversão de lucro
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl
    except: return None, None, 5.50

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ Radar Estratégico")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    if 'monitor_v90' not in st.session_state: st.session_state.monitor_v90 = {}
    
    st.divider()
    t_in = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
    v_brl = st.number_input("Valor Investido (R$):", min_value=0.0, step=100.0)
    p_in = st.number_input("Preço de Compra (Unidade):", min_value=0.0)
    p_out = st.number_input("Preço Alvo de Venda:", min_value=0.0)
    
    if st.button("🚀 Ativar Monitoramento"):
        if t_in:
            # FIX: Dicionário blindado contra KeyError 'investido' (image_251d5e.jpg)
            st.session_state.monitor_v90[t_in] = {
                "valor_total": v_brl, 
                "custo_unitario": p_in, 
                "alvo": p_out
            }
            st.rerun()

    if st.button("🗑️ Limpar Radar"):
        st.session_state.monitor_v90 = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Monitoramento Global Online")

if not st.session_state.monitor_v90:
    st.info("Radar pronto e limpo. Adicione ativos na lateral para iniciar.")
else:
    for t, cfg in st.session_state.monitor_v90.items():
        h, info, dolar = buscar_v90(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            is_usd = "-" in h.index.name or any(x in t.upper() for x in ["BTC", "XRP"])
            moeda = "US$" if is_usd else "R$"
            
            # Calculadora de Lucro em Reais (image_251d5e.jpg)
            inv = cfg.get("valor_total", 0)
            comp = cfg.get("custo_unitario", 1)
            
            # Se for cripto, converte cota para dólar para saber lucro em reais
            total_cotas = inv / (comp * (dolar if is_usd else 1)) if comp > 0 else 0
            v_atual_brl = total_cotas * (p_ag
