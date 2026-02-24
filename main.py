import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master (Foco em Estabilidade)
st.set_page_config(page_title="Nexus Master | Sandro", layout="wide")
st.markdown("<style>.stMetric { background-color: #161b22 !important; border-radius: 12px; padding: 15px; border: 1px solid #30363d; }</style>", unsafe_allow_html=True)

# 2. Comando Nexus
with st.sidebar:
    st.title("🛡️ Nexus Master")
    ticker_input = st.text_input("Ticker (VULC3, BTC-USD):", value="VULC3").upper()
    # Lógica Blindada: Adiciona .SA apenas se não for Cripto
    if "-" in ticker_input or len(ticker_input) > 5:
        ticker_final = ticker_input
    else:
        ticker_final = ticker_input + ".SA" if not ticker_input.endswith(".SA") else ticker_input
        
    meta_renda = st.number_input("Meta de Renda Mensal (R$):", value=1000.0)
    st.info("Status: Online (Cloud Ativa)")

# 3. Motor de Dados Ultraleve
try:
    df = yf.download(ticker_final, period="60d", interval="1d", progress=False)
    
    if not df.empty:
        # Garantindo valores únicos para não travar a formatação
        p_atual = float(df['Close'].iloc[-1])
        
        st.title(f"🚀 Inteligência Master: {ticker_input}")
        
        # --- BLOCO 1: RENDA E METAS ---
        c1, c2, c3 = st.columns(3)
        dy_est = 12.0 # Dividend Yield estimado para cálculos
        cap_necessario = (meta_renda * 12) / (dy_est / 100)
        
        c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
        c2.metric("Capital p/ Meta", f"R$ {cap_necessario:,.2f}")
        c3.metric("Renda Mensal Alvo", f"R$ {meta_renda:,.2f}")

        # --- BLOCO 2: RADAR TRADER (DAY & SWING) ---
        st.divider()
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.error("⚡ ESTRATÉGIA DAY TRADE")
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            st.write(f"**Resistência (Topo):** R$ {res:.2f}")
            st.write(f"**Suporte (Fundo):** R$ {sup:.2f}")
            st.caption("Alvo rápido de volatilidade (Invest10)")

        with col_b:
            st.success("📈 ESTRATÉGIA SWING TRADE")
            alvo_15 = p_atual * 1.15
            st.write(f"**Alvo Técnico (+15%):** R$ {alvo_15:.2f}")
            st.write(f"**Tendência:** {'Alta' if p_atual > df['Close'].mean() else 'Baixa'}")
            st.caption("Tendência de médio prazo (Folhainvest)")

        # 4. Gráfico Master (Sempre visível)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning(f"Buscando dados de {ticker_final}...")
except Exception as e:
    st.error("Ocorreu um erro na busca. Verifique o Ticker.")
