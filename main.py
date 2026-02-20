import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Ultra Contraste (Fim das cores transparentes)
st.set_page_config(page_title="InvestSmart Pro | Elite Trader", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-weight: bold; }
    .stInfo { background-color: #0a0d12 !important; color: #ffffff !important; border: 1px solid #00ff88 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Alerta e Teses
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

TESES = {
    "OHI": "🏘️ REIT de Saúde (EUA). Dono de hospitais e asilos. Renda sólida pelo envelhecimento da população.",
    "BBAS3": "🏦 Banco do Brasil. Foco em Agronegócio. Excelente pagadora de dividendos e muito sólida.",
    "BTC-USD": "🪙 Bitcoin. O 'Ouro Digital'. Reserva de valor escassa contra a inflação global."
}

# --- SIDEBAR: COMANDO DO TRADER ---
with st.sidebar:
    st.title("🛡️ Centro de Comando")
    token_bot = st.text_input("Token do seu Bot:", type="password")
    chat_id = st.text_input("Seu ID de Usuário (8392660003):")
    
    st.divider()
    modo = st.radio("Escolha o Modo de Operação:", ["🏛️ Carteira de Renda", "⚡ Swing Trade (Gráfico Kandall)"])

# --- MODO 1: CARTEIRA DE RENDA (ESTILO INVESTIDOR 10) ---
if modo == "🏛️ Carteira de Renda":
    st.title("🏛️ Central de Renda e Dividendos")
    col_renda = st.columns(3)
    ativos = ["BBAS3", "OHI", "JEPP34"]
    
    for i, t in enumerate(ativos):
        with col_renda[i % 3]:
            ticker = yf.Ticker(f"{t}.SA" if ".SA" not in t and "-" not in t else t)
            hist = ticker.history(period="5d", interval="1h")
            if not hist.empty:
                atual = hist['Close'].iloc[-1]
                dy = ticker.info.get('trailingAnnualDividendRate', 0)
                st.metric(f"💰 {t}", f"R$ {atual:,.2f}")
                st.write(f"📅 **Dividendos/Ano:** R$ {dy:,.2f}")
                st.info(f"**Mentor:** {TESES.get(t, 'Ativo sólido em monitoramento.')}")
    st.rerun()

# --- MODO 2: SWING TRADE (GRÁFICO KANDALL PROFISSIONAL) ---
else:
    st.title("⚡ Terminal Swing Trade | Análise Kandall")
    ticker_trade = st.text_input("Digite a Ação para Analisar (Ex: PETR4, VULC3, VALE3):", "PETR4").upper()
    
    t_s = f"{ticker_trade}.SA" if "-" not in ticker_trade and ".SA" not in ticker_trade else ticker_trade
    ticker = yf.Ticker(t_s)
    hist = ticker.history(period="60d", interval="1d") # Gráfico diário para Swing Trade
    
    if not hist.empty:
        # Médias Móveis (Estratégia de Especialista)
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        atual = hist['Close'].iloc[-1]
        
        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric(ticker_trade, f"R$ {atual:,.2f}")
            st.subheader("🤖 Mentor Trader")
            
            # Lógica de Veredito (Corrigida sem erros de sintaxe)
            if hist['MA9'].iloc[-1] > hist['MA20'].iloc[-1] and atual > hist['MA9'].iloc[-1]:
                st.success("🚀 GATILHO DE COMPRA! Tendência de alta confirmada com médias cruzadas.")
                enviar_alerta(token_bot, chat_id, f"🎯 COMPRA EM {ticker_trade}: Preço {atual}")
            elif atual < hist['MA20'].iloc[-1]:
                st.error("⚠️ GATILHO DE VENDA! O preço perdeu a tendência de alta. Proteja o capital.")
            else:
                st.warning("⚖️ AGUARDE. O ativo está em consolidação lateral sem tendência definida.")

        with c2:
            # Gráfico de Candles de Alta Definição
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Kandall'), row=1, col=1)
            fig.add_trace(go.Scatter
