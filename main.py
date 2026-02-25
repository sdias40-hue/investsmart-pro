import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Padronização Visual Sandro Master (Visibilidade Total)
st.set_page_config(page_title="Nexus Ultra | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 2px solid #00d4ff !important; border-radius: 12px; padding: 20px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    [data-testid="stMetricDelta"] { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Painel de Investimentos
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Command</h2>", unsafe_allow_html=True)
    ticker_mon = st.text_input("Monitorar Ativo:", value="VULC3").upper()
    
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Gestão de Carteira</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor Total Investido (R$):", value=0.0)
    preco_entrada = st.number_input("Preço Médio de Compra:", value=0.0, format="%.2f")
    alvo_saida = st.number_input("Alvo de Saída/Venda:", value=0.0, format="%.2f")
    
    if st.sidebar.button("🚀 Atualizar Monitor"):
        st.rerun()

# 3. Motor de Dados Anti-Travamento
ticker_f = ticker_mon + ".SA" if len(ticker_mon) < 6 and "." not in ticker_mon else ticker_mon

@st.cache_data(ttl=60) # Cache para não travar a conexão
def busca_dados(t):
    return yf.download(t, period="60d", interval="1d", progress=False)

try:
    df = busca_dados(ticker_f)
    
    if not df.empty:
        p_atual = float(df['Close'].iloc[-1])
        st.markdown(f"<h1>🚀 Terminal Master: <span class='neon-blue'>{ticker_mon}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE PERFORMANCE (LUCRO/PREJUÍZO) ---
        c1, c2, c3 = st.columns(3)
        quantidade = val_investido / preco_entrada if preco_entrada > 0 else 0
        resultado_r = (p_atual - preco_entrada) * quantidade if preco_entrada > 0 else 0
        var_per = ((p_atual / preco_entrada) - 1) * 100 if preco_entrada > 0 else 0
        
        c1.metric("Cotação Atual", f"R$ {p_atual:,.2f}")
        c2.metric("Resultado (R$)", f"R$ {resultado_r:,.2f}", delta=f"{var_per:.2f}%")
        c3.metric("Alvo de Saída", f"R$ {alvo_saida:,.2f}")

        # --- SISTEMA DE ABAS ---
        tab_graf, tab_estrat, tab_ia = st.tabs(["🎯 Gráfico Master", "⚡ Estratégias", "🧠 Estudo da IA"])

        with tab_graf:
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_estrat:
            st.markdown("<h3 class='neon-blue'>⚡ Radar de Operação</h3>", unsafe_allow_html=True)
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            st.metric("Resistência (Venda Rápida)", f"R$ {res:.2f}")
            st.metric("Suporte (Compra Segura)", f"R$ {sup:.2f}")

        with tab_ia:
            st.markdown("<h3 class='neon-blue'>🧠 Estudo Independente</h3>", unsafe_allow_html=True)
            ticker_ia = st.text_input("Ticker para a IA Pensar (ex: BTC-USD):", key="ia_input").upper()
            if ticker_ia:
                ia_data = yf.Ticker(ticker_ia).history(period="5d")
                if not ia_data.empty:
                    st.success(f"Relatório Master Nexus para {ticker_ia}")
                    st.write(f"O ativo está em R$ {ia_data['Close'].iloc[-1]:.2f}. Suporte de 5 dias em R$ {ia_data['Low'].min():.2f}.")
    else:
        st.warning("Aguardando dados... Se for Cripto, use o formato BTC-USD.")

except Exception:
    st.error("Sincronizando com a Nuvem... tente novamente em instantes.")
