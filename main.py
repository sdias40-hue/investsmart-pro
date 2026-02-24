import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master (Estilo Bloomberg Green)
st.set_page_config(page_title="Nexus Pro Master | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF41 !important; }
    /* Força todas as fontes para Verde Neon */
    h1, h2, h3, span, label, p { color: #00FF41 !important; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00FF41 !important; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #00FF41 !important; font-size: 2rem !important; }
    /* Abas Profissionais */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111; border: 1px solid #333; color: #00FF41 !important;
        border-radius: 5px 5px 0 0; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral
with st.sidebar:
    st.title("🛡️ Nexus Command")
    user_id = st.text_input("Usuário:", value="Sandro_Master")
    ticker_input = st.text_input("Ativo (VULC3, BTC-USD):", value="VULC3").upper()
    
    # Detector de Ativo (Evita travar se mercado fechar)
    if "-" in ticker_input or len(ticker_input) > 6:
        ticker = ticker_input
    else:
        ticker = ticker_input + ".SA" if not ticker_input.endswith(".SA") else ticker_input

    meta_renda = st.number_input("Meta Mensal (R$):", value=1000.0)
    st.success(f"Logado: {user_id}")

# 3. Motor de Dados Ultraleve (Funciona com mercado fechado)
try:
    # Usamos o Ticker simples para pegar o fechamento anterior se o mercado estiver off
    data_raw = yf.Ticker(ticker)
    df = data_raw.history(period="100d")
    
    if not df.empty:
        p_atual = float(df['Close'].iloc[-1])
        st.title(f"📊 Terminal Nexus: {ticker_input}")

        # --- ABAS DE OPERAÇÃO ---
        tab_mon, tab_day, tab_swing = st.tabs(["🎯 Monitor Master", "⚡ Day Trade", "📈 Swing Trade"])

        with tab_mon:
            c1, c2, c3 = st.columns(3)
            dy_base = 12.5 if ".SA" in ticker else 0
            cap_p_meta = (meta_renda * 12) / (dy_base / 100) if dy_base > 0 else 0
            
            c1.metric("Preço Agora", f"R$ {p_atual:,.2f}")
            c2.metric("DY Est.", f"{dy_base}%")
            c3.metric("Capital p/ Meta", f"R$ {cap_p_meta:,.0f}")
            
            # Gráfico Master
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Preço")])
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), name="Média 20d", line=dict(color='#00FF41', width=1)))
            fig.update_layout(template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_day:
            st.subheader("⚡ Radar Day Trade")
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            st.metric("Resistência (Venda)", f"R$ {res:.2f}")
            st.metric("Suporte (Compra)", f"R$ {sup:.2f}")

        with tab_swing:
            st.subheader("📈 Radar Swing Trade")
            st.metric("Alvo Técnico (+15%)", f"R$ {p_atual * 1.15:.2f}")
            st.info("💡 Análise baseada no último fechamento disponível.")

    else:
        st.warning("Aguardando abertura do mercado ou ticker inválido.")

except Exception as e:
    st.error("Sincronizando com a B3/Yahoo Finance...")
