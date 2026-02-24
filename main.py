import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Interface "Bloomberg Green"
st.set_page_config(page_title="Nexus Pro Master | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Fundo escuro e fontes verdes para máxima legibilidade */
    .main { background-color: #050505; color: #00FF41; }
    h1, h2, h3, p { color: #00FF41 !important; font-family: 'Courier New', Courier, monospace; }
    
    /* Customização dos Cards e Métricas */
    .stMetric { 
        background-color: #0a0a0a !important; 
        border: 1px solid #00FF41 !important; 
        border-radius: 10px; 
        padding: 15px; 
    }
    [data-testid="stMetricValue"] { color: #00FF41 !important; }
    
    /* Abas Estilizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111;
        border: 1px solid #333;
        color: #888;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF41 !important;
        color: black !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral (Configurações do Usuário)
with st.sidebar:
    st.title("🛡️ Nexus Master")
    user_id = st.text_input("Usuário:", value="Sandro_Master")
    ticker_input = st.text_input("Ativo (VULC3, BTC-USD, PETR4):", value="VULC3").upper()
    
    # Tratamento de Ticker para evitar erros de busca
    if "-" in ticker_input or len(ticker_input) > 6:
        ticker = ticker_input
    else:
        ticker = ticker_input + ".SA" if not ticker_input.endswith(".SA") else ticker_input

    meta_renda = st.number_input("Meta Mensal (R$):", value=1000.0)
    st.divider()
    st.success(f"Conectado: {user_id}")

# 3. Motor de Inteligência Estabilizado
try:
    # Busca dados (progress=False evita poluição visual no log)
    df = yf.download(ticker, period="100d", interval="1d", progress=False)
    
    if not df.empty:
        # Pega valores únicos para evitar erro de "Series"
        p_atual = float(df['Close'].iloc[-1])
        st.title(f"📊 Terminal Nexus: {ticker_input}")

        # --- ABAS DE ANÁLISE ---
        tab_mon, tab_day, tab_swing = st.tabs(["🎯 Monitor Master", "⚡ Day Trade", "📈 Swing Trade"])

        with tab_mon:
            c1, c2, c3 = st.columns(3)
            dy_est = 12.5 if ".SA" in ticker else 0
            cap_p_meta = (meta_renda * 12) / (dy_est / 100) if dy_est > 0 else 0
            
            c1.metric("Preço Agora", f"R$ {p_atual:,.2f}")
            c2.metric("DY Estimado", f"{dy_est}%" if dy_est > 0 else "N/A")
            c3.metric("Capital p/ Meta", f"R$ {cap_p_meta:,.0f}" if cap_p_meta > 0 else "---")
            
            # Gráfico com Linhas de Tendência (Média 20d)
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Preço")])
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), name="Média 20d", line=dict(color='#00FF41', width=1)))
            fig.update_layout(template="plotly_dark", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_day:
            st.subheader("⚡ Operação de Alta Frequência")
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            
            d_col1, d_col2 = st.columns(2)
            d_col1.metric("Venda (Resistência)", f"R$ {res:.2f}")
            d_col2.metric("Compra (Suporte)", f"R$ {sup:.2f}")
            st.info(f"💡 **Insight Nexus:** Ativo com volatilidade de {((res/sup)-1)*100:.2f}% nos últimos 5 dias.")

        with tab_swing:
            st.subheader("📈 Estratégia de Tendência")
            s_col1, s_col2 = st.columns(2)
            alvo = p_atual * 1.15
            
            s_col1.metric("Alvo Técnico (+15%)", f"R$ {alvo:.2f}")
            tendencia = "ALTA" if p_atual > df['Close'].mean() else "BAIXA"
            s_col2.metric("Trend Principal", tendencia)
            st.success(f"💎 **Análise Invest10:** Sugestão de aporte baseado em tendência de {tendencia}.")

    else:
        st.error(f"⚠️ Ativo {ticker_input} não encontrado. Verifique se o código está correto.")

except Exception as e:
    st.warning("Aguardando sincronização de mercado...")
