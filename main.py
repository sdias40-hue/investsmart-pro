import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. CSS de Ultra Contraste (Fim definitivo das cores apagadas)
st.set_page_config(page_title="InvestSmart Pro | Custom", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 8px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-weight: bold; }
    .stInfo { background-color: #0a0d12 !important; color: #ffffff !important; border: 1px solid #00ff88 !important; }
    .stAlert { background-color: #161b22 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte e Alerta
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

def buscar_dados_v77(t, p="1d", i="1m"):
    try:
        # Tenta várias combinações para garantir que BDRs e Criptos apareçam
        tickers_tentar = [f"{t}.SA", t, t.replace(".SA", "")]
        for ticker_str in tickers_tentar:
            ticker = yf.Ticker(ticker_str)
            hist = ticker.history(period=p, interval=i)
            if not hist.empty:
                return hist, ticker.info
        return None, None
    except: return None, None

# --- SIDEBAR: GESTÃO DE CARTEIRA ---
with st.sidebar:
    st.title("🛡️ Centro de Comando")
    token_bot = st.text_input("Token do Bot:", type="password")
    chat_id = st.text_input("Seu ID (8392660003):")
    
    st.divider()
    modo = st.radio("Selecione o Terminal:", ["🏛️ Prateleira de Renda", "⚡ Swing Trade (Kandall)"])
    
    st.divider()
    st.subheader("➕ Gerenciar Radar")
    novo_ativo = st.text_input("Adicionar Ticker (Ex: PETR4, OHI, BTC-USD):").upper()
    
    # Sistema de Memória da Carteira
    if 'carteira' not in st.session_state:
        st.session_state.carteira = [] # Começa vazio como você pediu
        
    if st.button("Adicionar ao Radar") and novo_ativo:
        if novo_ativo not in st.session_state.carteira:
            st.session_state.carteira.append(novo_ativo)
            st.success(f"{novo_ativo} adicionado!")

    if st.button("Limpar Radar"):
        st.session_state.carteira = []
        st.rerun()

# --- MODO 1: PRATELEIRA DE RENDA ---
if modo == "🏛️ Prateleira de Renda":
    st.title("🏛️ Sua Prateleira de Renda Personalizada")
    
    if not st.session_state.carteira:
        st.info("👋 Seu radar está vazio. Adicione ativos na barra lateral para começar o monitoramento.")
    else:
        # Organiza em grade de 3 colunas
        cols = st.columns(3)
        for i, t in enumerate(st.session_state.carteira):
            with cols[i % 3]:
                hist, info = buscar_dados_v77(t, "5d", "1h")
                if hist is not None:
                    atual = hist['Close'].iloc[-1]
                    dy = info.get('trailingAnnualDividendRate', 0)
                    st.metric(f"💰 {t}", f"R$ {atual:,.2f}")
                    st.caption(f"📅 Renda Anual: R$ {dy:,.2f}")
                    st.info(f"**Análise:** {info.get('sector', 'Ativo Global')}. Foco em solidez e dividendos.")
                else:
                    st.error(f"Erro ao carregar {t}. Verifique o código.")
    st.divider()

# --- MODO 2: SWING TRADE (KANDALL) ---
else:
    st.title("⚡ Terminal Swing Trade | Análise Profissional")
    
    if not st.session_state.carteira:
        st.info("👋 Adicione ativos no radar lateral para analisar o gráfico de Swing Trade.")
    else:
        ticker_trade = st.selectbox("Ativo para Analisar:", st.session_state.carteira)
        hist, info = buscar_dados_v77(ticker_trade, "60d", "1d")
        
        if hist is not None:
            # Médias e Gatilhos
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA9'] = hist['Close'].rolling(window=9).mean()
            atual = hist['Close'].iloc[-1]
            
            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric(ticker_trade, f"R$ {atual:,.2f}")
                st.subheader("🤖 Mentor Trader")
                if hist['MA9'].iloc[-1] > hist['MA20'].iloc[-1]:
                    st.success("🚀 GATILHO: Compra! Tendência de alta forte.")
                    enviar_alerta(token_bot, chat_id, f"🎯 SINAL COMPRA: {ticker_trade} em {atual}")
                else:
                    st.error("⚠️ GATILHO: Venda ou Aguarde. Tendência de baixa.")
                st.info(f"Analisando {ticker_trade} do setor de {info.get('sector', 'Tecnologia/Global')}.")

            with c2:
                # Gráfico de Candles (Kandall) de Alta Definição
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
                fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Kandall'), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], name='Média 20d', line=dict(color='#00ff88')), row=1, col=1)
                
                cores_v = ['#00ff88' if hist.Close[i] >= hist.Open[i] else '#ff4b4b' for i in range(len(hist))]
                fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=cores_v, name='Volume'), row=2, col=1)
                
                fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=600, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

    time.sleep(30)
    st.rerun()
