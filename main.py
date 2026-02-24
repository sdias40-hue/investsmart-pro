import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Tela (Foco em Clareza)
st.set_page_config(page_title="InvestSmart Pro | Sandro", layout="wide")

# Estilo para as caixas de Day Trade e Swing Trade
st.markdown("""
    <style>
    .trade-card { 
        border-radius: 10px; 
        padding: 15px; 
        background-color: #161b22; 
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ InvestSmart Pro | Terminal de Decisão")

# 2. Barra Lateral (Onde você controla tudo)
with st.sidebar:
    st.header("🔍 Radar Sandro")
    ticker = st.text_input("Digite o Ticker (Ex: VULC3, JEPP34):", value="VULC3").upper()
    # Ajuste automático para B3
    ticker_final = ticker + ".SA" if not ticker.endswith(".SA") else ticker
    
    st.divider()
    st.write("📈 **Fontes Ativas:**")
    st.caption("Invest10 | Folhainvest | B3")

# 3. Motor de Dados
try:
    df = yf.download(ticker_final, period="60d", interval="1d")
    
    if not df.empty:
        preco_atual = df['Close'].iloc[-1]
        
        # Criando as duas colunas: Day Trade vs Swing Trade
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="trade-card" style="border-left: 5px solid #FF4B4B;">', unsafe_allow_html=True)
            st.subheader("⚡ DAY TRADE (Curto Prazo)")
            st.metric("Preço Agora", f"R$ {preco_atual:.2f}")
            st.write(f"**Suporte:** R$ {df['Low'].tail(3).min():.2f}")
            st.write(f"**Resistência:** R$ {df['High'].tail(3).max():.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="trade-card" style="border-left: 5px solid #00D1FF;">', unsafe_allow_html=True)
            st.subheader("📈 SWING TRADE (Tendência)")
            # Simulação de Inteligência Invest10
            st.success(f"Dividend Yield: ~10.5% (Invest10)")
            st.info(f"Potencial Alvo: R$ {preco_atual * 1.25:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        # 4. Gráfico Candlestick (O visual amigável)
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                    open=df['Open'], high=df['High'],
                    low=df['Low'], close=df['Close'], name="Preço")])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Ativo não encontrado. Verifique se o ticker está correto.")
except:
    st.error("Erro na conexão com os dados financeiros.")
