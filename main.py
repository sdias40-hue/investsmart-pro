import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Setup Visual Sandro Pro
st.set_page_config(page_title="InvestSmart Pro | Terminal Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22 !important; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .status-box { padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar de Radar
with st.sidebar:
    st.title("🛡️ Nexus Command")
    ticker = st.text_input("Ticker (Ex: VULC3, JEPP34):", value="VULC3").upper()
    ticker_final = ticker + ".SA" if not ticker.endswith(".SA") else ticker
    meta_renda = st.number_input("Meta Renda Mensal (R$):", value=1000.0)
    st.divider()
    st.caption("Fontes: B3, Invest10, Folhainvest")

# 3. Motor de Inteligência Real
try:
    acao = yf.Ticker(ticker_final)
    hist = acao.history(period="60d")
    info = acao.info
    
    if not hist.empty:
        p_atual = hist['Close'].iloc[-1]
        
        # CÁLCULOS DE EFICIÊNCIA (Fugindo dos R$ 86 mil)
        dy = info.get('dividendYield', 0) * 100
        lpa = info.get('trailingEps', 0)
        vpa = info.get('bookValue', 0)
        # Preço Justo (Graham)
        preco_justo = (22.5 * lpa * vpa)**0.5 if lpa > 0 and vpa > 0 else 0
        
        st.title(f"🔍 Nexus Intelligence: {ticker}")
        
        # 4. Painel de Indicadores Principais
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Preço Atual", f"R$ {p_atual:.2f}")
        col2.metric("Preço Justo (Graham)", f"R$ {preco_justo:.2f}", f"{((preco_justo/p_atual)-1)*100:.1f}%" if preco_justo > 0 else "0%")
        col3.metric("Dividend Yield", f"{dy:.2f}%")
        col4.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%")

        # 5. Divisão de Operação (Day vs Swing)
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown('<div class="status-box" style="border-left: 5px solid #FF4B4B;"><h4>⚡ Foco DAY TRADE</h4></div>', unsafe_allow_html=True)
            suporte = hist['Low'].tail(3).min()
            resistencia = hist['High'].tail(3).max()
            st.write(f"🚀 **Ponto de Escapada:** R$ {resistencia:.2f}")
            st.write(f"🛑 **Stop Seguro:** R$ {suporte:.2f}")
            
        with col_b:
            st.markdown('<div class="status-box" style="border-left: 5px solid #00D1FF;"><h4>📈 Foco SWING TRADE</h4></div>', unsafe_allow_html=True)
            aporte_meta = meta_renda / (dy/100/12) if dy > 0 else 0
            st.write(f"💰 **Para Renda de R$ {meta_renda}:** Aporte de R$ {aporte_meta:,.2f}")
            st.write(f"🎯 **Alvo Técnico:** R$ {p_atual * 1.2:.2f} (20% upside)")

        # 6. Gráfico de Candlestick
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close)])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    else: st.error("Ativo não encontrado.")
except: st.error("Erro ao conectar com a B3.")
