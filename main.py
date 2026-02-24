import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master de Alta Precisão
st.set_page_config(page_title="Nexus Master | Sandro", layout="wide")
st.markdown("<style>.stMetric { background-color: #161b22 !important; border-radius: 12px; padding: 20px; border: 1px solid #30363d; }</style>", unsafe_allow_html=True)

# 2. Comando Lateral
with st.sidebar:
    st.title("🛡️ Nexus Master")
    ticker = st.text_input("Ticker Ativo:", value="VULC3").upper()
    ticker_final = ticker + ".SA" if not ticker.endswith(".SA") and len(ticker) <= 6 else ticker
    meta_renda = st.number_input("Meta de Renda Mensal (R$):", value=1000.0)
    st.info("Status: Online (Cloud Ativa)")

# 3. Motor de Dados Estabilizado
try:
    # Busca direta sem frescura para não cair a conexão
    df = yf.download(ticker_final, period="60d", interval="1d")
    
    if not df.empty:
        p_atual = df['Close'].iloc[-1]
        
        # --- BLOCO MASTER: RENDA ---
        st.title(f"🚀 Inteligência Master: {ticker}")
        
        # Simulação de Dividend Yield (Para evitar erro de conexão com info)
        dy_simulado = 12.5 # Valor base para cálculo de meta
        investimento_necessario = (meta_renda * 12) / (dy_simulado / 100)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Preço Atual", f"R$ {p_atual:.2f}")
        c2.metric("Capital p/ Renda", f"R$ {investimento_necessario:,.2f}")
        c3.metric("Renda Alvo", f"R$ {meta_renda:,.2f}")

        # --- BLOCO TRADER: DAY & SWING (O que faltava) ---
        st.divider()
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.error("⚡ ESTRATÉGIA DAY TRADE")
            st.write(f"**Resistência (Topo):** R$ {df['High'].tail(5).max():.2f}")
            st.write(f"**Suporte (Fundo):** R$ {df['Low'].tail(5).min():.2f}")
            st.caption("Foco: Movimentos rápidos de 24h")

        with col_b:
            st.success("📈 ESTRATÉGIA SWING TRADE")
            st.write(f"**Alvo Técnico:** R$ {p_atual * 1.15:.2f}")
            st.write(f"**Tendência:** {'Alta' if p_atual > df['Close'].mean() else 'Baixa'}")
            st.caption("Foco: Tendência Semanal")

        # 4. Gráfico Master
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("Aguardando dados da B3... Verifique o Ticker.")
except Exception as e:
    st.error(f"Erro Master: {e}")
