import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Estética Master High Clarity
st.set_page_config(page_title="Nexus Master | Sandro", layout="wide")
st.markdown("<style>.stMetric { background-color: #161b22 !important; border-radius: 12px; padding: 20px; border: 1px solid #30363d; }</style>", unsafe_allow_html=True)

# 2. Sidebar Nexus
with st.sidebar:
    st.title("🛡️ Nexus Master")
    ticker = st.text_input("Ticker Ativo:", value="VULC3").upper()
    ticker_final = ticker + ".SA" if not ticker.endswith(".SA") and len(ticker) <= 6 else ticker
    meta_renda = st.number_input("Meta de Renda (R$):", value=1000.0)
    st.divider()
    st.info("Status: Online (Cloud Ativa)")

# 3. Processamento Master
try:
    acao = yf.Ticker(ticker_final)
    hist = acao.history(period="90d")
    info = acao.info
    
    if not hist.empty:
        p_atual = hist['Close'].iloc[-1]
        dy = info.get('dividendYield', 0) * 100
        
        # --- BLOCO 1: RENDA E DIVIDENDOS (O QUE VOCÊ JÁ TEM) ---
        st.title(f"🚀 Inteligência Master: {ticker}")
        c1, c2, c3 = st.columns(3)
        
        # Cálculo de Aportes Fugindo dos 86 mil
        aporte_necessario = (meta_renda / (dy/100/12)) if dy > 0 else 0
        
        c1.metric("Preço Atual", f"R$ {p_atual:.2f}")
        c2.metric("Dividend Yield", f"{dy:.2f}%")
        c3.metric("Capital p/ Meta", f"R$ {aporte_necessario:,.2f}")

        # --- BLOCO 2: INFORMAÇÕES DE TRADER (O QUE FALTAVA) ---
        st.divider()
        st.subheader("📊 Radar de Operações (Day & Swing)")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.error("⚡ ESTRATÉGIA DAY TRADE")
            st.write(f"**Resistência (Venda):** R$ {hist['High'].tail(5).max():.2f}")
            st.write(f"**Suporte (Compra):** R$ {hist['Low'].tail(5).min():.2f}")
            st.caption("Foco: Entradas e saídas rápidas (Invest10)")

        with col_b:
            st.success("📈 ESTRATÉGIA SWING TRADE")
            st.write(f"**Alvo Técnico:** R$ {p_atual * 1.15:.2f}")
            st.write(f"**P/VP (Valor):** {info.get('priceToBook', 'N/A')}")
            st.caption("Foco: Valorização e Dividendos (Folhainvest)")

        # 4. Gráfico de Candlestick
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close)])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    else: st.error("Ativo não encontrado.")
except: st.error("Erro na conexão Master.")
