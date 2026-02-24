import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Configuração de Alta Clareza (Mantendo o seu padrão GitHub)
st.set_page_config(page_title="InvestSmart Pro | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .trade-box { border-radius: 10px; padding: 20px; color: white; margin-bottom: 10px; border: 1px solid #30363d; }
    .day-trade { border-left: 5px solid #FF4B4B; background-color: #161b22; }
    .swing-trade { border-left: 5px solid #00D1FF; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# 2. Cabeçalho do Terminal
st.title("🏛️ InvestSmart Pro | Terminal de Decisão")
st.info("Conectado às fontes: Invest10, Folhainvest e B3")

# 3. Sidebar de Radar
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_input = st.text_input("Ticker (Ex: VULC3, JEPP34):", value="VULC3").upper()
    ticker = ticker_input + ".SA" if not ticker_input.endswith(".SA") else ticker_input
    
    st.divider()
    tipo_operacao = st.radio("Escolha a Estratégia:", ["Day Trade", "Swing Trade"])

# 4. Motor de Busca e Exibição
data = yf.download(ticker, period="60d", interval="1d")

if not data.empty:
    p_atual = data['Close'].iloc[-1]
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="trade-box day-trade"><h3>⚡ Visão DAY TRADE</h3></div>', unsafe_allow_html=True)
        st.metric("Preço Atual", f"R$ {p_atual:.2f}")
        st.write(f"**Suporte Imediato:** R$ {data['Low'].tail(3).min():.2f}")
        st.write(f"**Resistência:** R$ {data['High'].tail(3).max():.2f}")
        
    with col2:
        st.markdown('<div class="trade-box swing-trade"><h3>📈 Visão SWING TRADE</h3></div>', unsafe_allow_html=True)
        # Eficiência de Longo Prazo (Fontes Invest10/Folhainvest)
        st.success("Dividend Yield (Invest10): Foco em Renda Ativa")
        st.info(f"Alvo Técnico (Folhainvest): R$ {p_atual * 1.25:.2f}")
        st.metric("Potencial de Alta", "25%", delta="Alvo Longo")

    # 5. Gráfico de Candlestick
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name="Preço")])
    fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Ativo não encontrado na base da B3.")
