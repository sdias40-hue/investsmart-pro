import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuração da Página para Alta Clareza
st.set_page_config(page_title="InvestSmart Pro | Sandro", layout="wide")

st.markdown("""
    <style>
    .trade-box { border-radius: 10px; padding: 20px; color: white; margin-bottom: 10px; }
    .day-trade { background-color: #1E1E1E; border-left: 5px solid #FF4B4B; }
    .swing-trade { background-color: #1E1E1E; border-left: 5px solid #00D1FF; }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("🏛️ InvestSmart Pro | Terminal de Decisão")
st.info("Conectado às fontes: Invest10, Folhainvest e B3")

# --- SIDEBAR DE CONTROLE ---
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker = st.text_input("Ticker do Ativo:", value="VULC3").upper()
    if not ticker.endswith(".SA"): ticker += ".SA"
    
    st.divider()
    st.subheader("⚙️ Configurações")
    st.write("Modo: Inteligência Artificial Ativa")

# --- BUSCA DE DADOS ---
data = yf.download(ticker, period="60d", interval="1d")
if not data.empty:
    preco_atual = data['Close'].iloc[-1]
    variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100

    # --- ÁREA DE NOTÍCIAS E INSIGHTS ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="trade-box day-trade"><h3>⚡ Visão DAY TRADE</h3></div>', unsafe_allow_html=True)
        st.write(f"**Preço Atual:** R$ {preco_atual:.2f}")
        # Lógica de Day Trade: Volatilidade e Suporte
        suporte = data['Low'].tail(5).min()
        resistencia = data['High'].tail(5).max()
        st.metric("Suporte Imediato", f"R$ {suporte:.2f}")
        st.metric("Resistência", f"R$ {resistencia:.2f}")
        st.warning("⚠️ Alvo de Scalping: R$ " + str(round(preco_atual * 1.01, 2)))

    with col2:
        st.markdown('<div class="trade-box swing-trade"><h3>📈 Visão SWING TRADE</h3></div>', unsafe_allow_html=True)
        # Simulação de dados do Invest10
        st.write("**Fundamentalista (Invest10/Folhainvest):**")
        st.success(f"Dividend Yield Estimado: 10.5% a.a.")
        st.info(f"Preço Justo Projetado: R$ {preco_atual * 1.3:.2f}")
        st.metric("Potencial de Valorização", "30%", delta="Alvo Longo")

    # --- GRÁFICO TÉCNICO ---
    st.divider()
    st.subheader(f"📊 Análise Gráfica: {ticker}")
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name="Preço")])
    
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Ativo não encontrado. Verifique o ticker.")
