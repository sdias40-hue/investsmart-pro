import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. VISIBILIDADE MASTER E RESPONSIVIDADE
st.set_page_config(page_title="Nexus Global | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, label, div { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important;
    }
    /* Estilo para Cards que funcionam em qualquer tela */
    .metric-card {
        background-color: #0a0a0a;
        border: 1px solid #00d4ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .status-box { 
        background-color: #0e1117; 
        border-left: 8px solid #00d4ff; 
        padding: 15px; 
        border-radius: 8px; 
        margin: 10px 0;
    }
    /* Ajuste de gráfico para não sumir no PC e caber no Celular */
    .stPlotlyChart { min-height: 400px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. RADAR GLOBAL (OPINIÃO MUNDIAL)
st.markdown("<h3 class='neon-blue'>🌍 Radar das Bolsas Mundiais</h3>", unsafe_allow_html=True)
indices = {"S&P 500 (EUA)": "^GSPC", "Nasdaq (Tech EUA)": "^IXIC", "Ibovespa (Brasil)": "^BVSP"}
# No celular, as colunas vão se empilhar automaticamente
cols = st.columns(len(indices))

for i, (nome, ticket) in enumerate(indices.items()):
    try:
        idx = yf.Ticker(ticket).history(period="2d")
        if len(idx) > 1:
            v_at = idx['Close'].iloc[-1]
            var = ((v_at / idx['Close'].iloc[-2]) - 1) * 100
            cols[i].metric(nome, f"{v_at:,.0f}", f"{var:.2f}%")
    except: pass

# 3. COMANDO LATERAL
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Global</h2>", unsafe_allow_html=True)
    t_in = st.text_input("Ativo (Ex: BTC-USD, VULC3, JEPQ34):", value="BTC-USD").upper()
    val_inv = st.number_input("Valor Investido (R$):", value=0.0)
    p_pago = st.number_input("Preço de Entrada (R$):", value=0.0, format="%.2f")
    st.sidebar.button("🚀 Sincronizar")

# 4. MOTOR DE INTELIGÊNCIA 24H
t_f = t_in + ".SA" if "-" not in t_in and "." not in t_in and len(t_in) < 6 else t_in

try:
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    if not data.empty:
        p_at = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{t_in}</span></h1>", unsafe_allow_html=True)

        # PERFORMANCE EM DUAS COLUNAS (FICA ÓTIMO NO CELULAR)
        c1, c2 = st.columns(2)
        lucro = (p_at - p_pago) * (val_inv / p_pago) if p_pago > 0 else 0
        c1.metric("Preço Agora", f"R$ {p_at:,.2f}")
        c2.metric("Meu Lucro", f"R$ {lucro:,.2f}", delta=f"{((p_at/p_pago)-1)*100:.2f}%" if p_pago > 0 else "0%")

        # VEREDITO DO ROBÔ (O QUE VOCÊ PEDIU)
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        tende = "ALTA" if p_at > data['Close'].mean() else "QUEDA"
        cor = "#00ff00" if tende == "ALTA" else "#ff4b4b"
        
        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor};'>
                <h4 style='color: {cor} !important;'>📢 RECOMENDAÇÃO: {tende}</h4>
                <p>Suporte em R$ {data['Low'].tail(10).min():.2f}. Se o S&P 500 (EUA) subir, a força de {t_in} aumenta.</p>
            </div>
        """, unsafe_allow_html=True)

        # GRÁFICO (RESTAURADO E RESPONSIVO)
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template
