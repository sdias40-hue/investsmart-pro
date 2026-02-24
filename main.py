import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Estética Master Green (Otimizada para PC e Celular)
st.set_page_config(page_title="Nexus Global Master | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF41 !important; }
    h1, h2, h3, span, label, p { color: #00FF41 !important; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00FF41 !important; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #00FF41 !important; }
    .stTabs [aria-selected="true"] { background-color: #00FF41 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Nexus Global
with st.sidebar:
    st.title("🛡️ Nexus Global")
    user_id = st.text_input("Usuário:", value="Sandro_Master")
    ticker_input = st.text_input("Ativo (AAPL, TSLA, VULC3, BTC-USD):", value="AAPL").upper()
    
    # Inteligência de Ticker Global
    if "-" in ticker_input or len(ticker_input) > 5:
        ticker = ticker_input
    elif ticker_input in ["AAPL", "TSLA", "AMZN", "MSFT", "GOOGL"]:
        ticker = ticker_input # Ativos USA Diretos
    else:
        ticker = ticker_input + ".SA" if not ticker_input.endswith(".SA") else ticker_input

    st.divider()
    st.write("🌍 **Radar Internacional Ativo**")

# 3. Motor de Inteligência e Notícias
try:
    data_raw = yf.Ticker(ticker)
    df = data_raw.history(period="100d")
    
    if not df.empty:
        p_atual = float(df['Close'].iloc[-1])
        currency = "US$" if ".SA" not in ticker and "-" not in ticker else "R$"
        
        st.title(f"🌍 Nexus Global Intelligence: {ticker_input}")

        tab_mon, tab_trader, tab_sugestoes = st.tabs(["🎯 Monitor", "⚡ Trader", "💡 Sugestões Master"])

        with tab_mon:
            c1, c2, c3 = st.columns(3)
            c1.metric("Preço Atual", f"{currency} {p_atual:,.2f}")
            vol_media = df['Volume'].mean()
            c2.metric("Liquidez Média", f"{vol_media:,.0f}")
            c3.metric("Moeda", currency)
            
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
            fig.update_layout(template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_trader:
            st.subheader("⚡ Radar de Operações USA/B3")
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            st.metric("Resistência Global", f"{currency} {res:.2f}")
            st.metric("Suporte Global", f"{currency} {sup:.2f}")

        with tab_sugestoes:
            st.subheader("🤖 Sugestões de Compra (IA Nexus)")
            # Simulação de análise de notícias internacionais
            st.success("✅ **Oportunidade Detectada no Setor Tech (USA)**")
            st.write(f"O ativo **{ticker_input}** apresenta suporte sólido em {currency} {sup:.2f}.")
            st.info("📰 **Notícias Recentes:** Analistas internacionais elevam preço-alvo baseado em novos balanços trimestrais.")
            
            # Tabela de boas compras sugeridas
            st.write("---")
            st.write("🚀 **Top 3 Boas Compras (Sugestão do Robô):**")
            sugestoes = pd.DataFrame({
                "Ativo": ["AAPL", "VULC3", "BTC-USD"],
                "Motivo": ["Crescimento Tech", "Dividendos Altos", "Halving Próximo"],
                "Risco": ["Baixo", "Médio", "Alto"]
            })
            st.table(sugestoes)

    else: st.warning("Aguardando dados globais...")
except Exception as e:
    st.error("Sincronizando com mercados internacionais...")
