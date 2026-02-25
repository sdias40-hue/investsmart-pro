import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. VISIBILIDADE MASTER (Resolve o problema do PC e Celular)
st.set_page_config(page_title="Nexus Global Trader | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, label, div { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; }
    .status-box { background-color: #0e1117; border: 1px solid #00d4ff; border-left: 10px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    /* Altura mínima para o gráfico não sumir no monitor do PC */
    .stPlotlyChart { min-height: 500px !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. RADAR GLOBAL (OPINIÃO SOBRE AS BOLSAS DO MUNDO)
st.markdown("<h3 class='neon-blue'>🌍 Radar das Bolsas Mundiais</h3>", unsafe_allow_html=True)
indices = {"S&P 500 (EUA)": "^GSPC", "Nasdaq (Tech EUA)": "^IXIC", "Ibovespa (Brasil)": "^BVSP"}
cols = st.columns(len(indices))

for i, (nome, ticket) in enumerate(indices.items()):
    idx = yf.Ticker(ticket).history(period="2d")
    if len(idx) > 1:
        v_atual = idx['Close'].iloc[-1]
        var = ((v_atual / idx['Close'].iloc[-2]) - 1) * 100
        cols[i].metric(nome, f"{v_atual:,.0f}", f"{var:.2f}%")

# 3. COMANDO LATERAL (GESTÃO DE CARTEIRA)
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Command</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD, VULC3, AAPL):", value="BTC-USD").upper()
    
    st.divider()
    is_crypto = "-" in ticker_input or len(ticker_input) > 6
    st.markdown(f"<p class='neon-blue'>Gestão: {'Cripto' if is_crypto else 'Ações'}</p>", unsafe_allow_html=True)
    
    val_investido = st.number_input("Quanto investi (R$):", value=0.0)
    preco_pago = st.number_input("Preço de Entrada (R$):", value=0.0, format="%.2f")

    if st.sidebar.button("🚀 Gerar Inteligência Master"):
        st.rerun()

# 4. MOTOR DE INTELIGÊNCIA LOCAL (Sem depender de Trigger.dev)
t_final = ticker_input + ".SA" if not is_crypto and "." not in ticker_input and len(ticker_input) < 6 else ticker_input

try:
    data = yf.download(t_final, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # PERFORMANCE
        c1, c2 = st.columns(2)
        lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        c1.metric("Preço Agora", f"R$ {p_atual:,.2f}")
        c2.metric("Lucro/Perda Real", f"R$ {lucro_r:,.2f}", delta=f"{((p_atual/preco_pago)-1)*100:.2f}%" if preco_pago > 0 else "0%")

        # VEREDITO DO ROBÔ
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito e Análise do Robô</h3>", unsafe_allow_html=True)
        tendencia = "ALTA" if p_atual > data['Close'].mean() else "QUEDA"
        cor_v = "#00ff00" if tendencia == "ALTA" else "#ff4b4b"

        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor_v};'>
                <h4 style='color: {cor_v} !important;'>📢 RECOMENDAÇÃO: {tendencia}</h4>
                <p><b>Análise Master:</b> O ativo está em ciclo de {tendencia}. Suporte forte em R$ {data['Low'].tail(10).min():.2f}.</p>
                <p><b>Influência Global:</b> Se os EUA (S&P 500) continuarem subindo, o ativo tende a buscar R$ {data['High'].tail(10).max():.2f}.</p>
            </div>
        """, unsafe_allow_html=True)

        # GRÁFICO (RESTAURADO PARA PC)
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else: st.warning("Digite um código válido... Ex: VULC3 ou BTC-USD")
except Exception: st.error("Erro de sincronização. Clique em Gerar Inteligência.")
