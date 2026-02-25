import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Padronização Ultra-Visível (PC e Celular)
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff !important; }
    /* Forçar visibilidade de todas as tags de texto */
    h1, h2, h3, h4, p, span, label, div { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.6rem !important; }
    .mentor-box { background-color: #0e1117; border-left: 5px solid #00d4ff; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-top: 1px solid #333; }
    /* Ajuste para o gráfico não sumir no PC */
    iframe { min-height: 400px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    ticker_mon = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Gestão de Carteira</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor Investido (R$):", value=0.0)
    preco_compra = st.number_input("Preço de Compra:", value=0.0, format="%.2f")
    
    if st.sidebar.button("🚀 Sincronizar Agora"):
        st.rerun()

# 3. Motor Mentor Estabilizado
t_f = ticker_mon + ".SA" if len(ticker_mon) < 6 and "." not in ticker_mon else ticker_mon

try:
    # Coletando 60 dias para ter uma linha de tendência melhor
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_mon}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE RESULTADO (LUCRO/PREJUÍZO) ---
        c1, c2 = st.columns(2)
        res_r = (p_atual - preco_compra) * (val_investido / preco_compra) if preco_compra > 0 else 0
        per_c = ((p_atual / preco_compra) - 1) * 100 if preco_compra > 0 else 0
        
        c1.metric("Preço de Hoje", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {res_r:,.2f}", delta=f"{per_c:.2f}%")

        # --- ORIENTAÇÃO DIRETA ---
        st.divider()
        st.markdown("<h3 class='neon-blue'>💡 O que fazer agora?</h3>", unsafe_allow_html=True)
        
        # Cálculos de Mentor (Topo e Fundo de 10 dias)
        topo = float(data['High'].tail(10).max())
        fundo = float(data['Low'].tail(10).min())
        
        col_compra, col_venda = st.columns(2)
        with col_compra:
            st.markdown(f"
