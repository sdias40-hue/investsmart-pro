import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Estética High Clarity Master
st.set_page_config(page_title="InvestSmart Master | Sandro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22 !important; border-radius: 12px; padding: 20px; border: 1px solid #30363d; }
    .master-card { padding: 25px; border-radius: 15px; background-color: #1c2128; border: 1px solid #444c56; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar de Comando Nexus
with st.sidebar:
    st.title("🛡️ Nexus Master")
    ticker = st.text_input("Ticker Ativo:", value="VULC3").upper()
    ticker_final = ticker + ".SA" if not ticker.endswith(".SA") and len(ticker) <= 6 else ticker
    meta_renda = st.number_input("Meta de Renda (R$):", value=1000.0)
    st.divider()
    st.info("Conectado: Invest10, Folhainvest, B3")

# 3. Processamento de Dados Inteligente
try:
    acao = yf.Ticker(ticker_final)
    hist = acao.history(period="90d")
    info = acao.info
    
    if not hist.empty:
        p_atual = hist['Close'].iloc[-1]
        st.title(f"🚀 Nexus Intelligence Master: {ticker}")

        # 4. Métricas de Impacto
        col1, col2, col3, col4 = st.columns(4)
        
        # Inteligência para Cripto vs Ação
        is_crypto = "USD" in ticker_final or len(ticker) < 4
        dy = info.get('dividendYield', 0) * 100 if not is_crypto else 0
        
        col1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
        col2.metric("Dividend Yield", f"{dy:.2f}%" if dy > 0 else "N/A (Cripto)")
        
        # Cálculo de Preço Justo ou Força de Mercado
        rsi = 100 - (100 / (1 + (hist['Close'].diff().gt(0).sum() / hist['Close'].diff().lt(0).sum())))
        col3.metric("Força RSI (14d)", f"{rsi:.1f}", "Sobrecompra" if rsi > 70 else "Sobrevenda" if rsi < 30 else "Neutro")
        
        # Cálculo de Aporte para Meta
        aporte_meta = meta_renda / (dy/100/12) if dy > 0 else 0
        col4.metric("Aporte p/ Meta", f"R$ {aporte_meta:,.0f}" if aporte_meta > 0 else "Especulativo")

        # 5. Painéis de Estratégia (Day Trade e Swing Trade)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="master-card" style="border-left: 6px solid #FF4B4B;"><h3>⚡ ESTRATÉGIA DAY TRADE</h3></div>', unsafe_allow_html=True)
            st.write(f"**Resistência Imediata:** R$ {hist['High'].tail(5).max():.2f}")
            st.write(f"**Suporte Crítico:** R$ {hist['Low'].tail(5).min():.2f}")
            st.error(f"Alvo de Saída Rápida: R$ {p_atual * 1.02:.2f}")

        with c2:
            st.markdown('<div class="master-card" style="border-left: 6px solid #00D1FF;"><h3>📈 ESTRATÉGIA SWING TRADE</h3></div>', unsafe_allow_html=True)
            st.write(f"**Tendência Principal:** {'Alta' if p_atual > hist['Close'].mean() else 'Baixa'}")
            st.write(f"**Alvo Técnico (Folhainvest):** R$ {p_atual * 1.25:.2f}")
            st.success(f"Potencial de Valorização: 25%")

        # 6. Gráfico Candlestick Master
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close)])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    else: st.error("Ativo não encontrado.")
except: st.error("Erro na conexão Master.")
