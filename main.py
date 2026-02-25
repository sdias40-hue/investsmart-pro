import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master (Visibilidade e Estabilidade)
st.set_page_config(page_title="Nexus Global | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, label, div { color: #ffffff !important; font-family: 'Segoe UI', sans-serif !important; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; }
    .status-box { background-color: #0e1117; border: 1px solid #00d4ff; border-left: 10px solid #00d4ff; padding: 20px; border-radius: 8px; }
    iframe { min-height: 500px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. RADAR GLOBAL (INFLUÊNCIA DAS BOLSAS MUNDIAIS)
st.markdown("<h3 class='neon-blue'>🌍 Radar das Bolsas Mundiais</h3>", unsafe_allow_html=True)
indices = {"S&P 500 (EUA)": "^GSPC", "Nasdaq (Tech)": "^IXIC", "Ibovespa (BR)": "^BVSP"}
cols = st.columns(3)

for i, (nome, ticket) in enumerate(indices.items()):
    idx_data = yf.Ticker(ticket).history(period="2d")
    if len(idx_data) > 1:
        v_atual = idx_data['Close'].iloc[-1]
        var = ((v_atual / idx_data['Close'].iloc[-2]) - 1) * 100
        cols[i].metric(nome, f"{v_atual:,.0f}", f"{var:.2f}%")

# 3. COMANDO LATERAL (GESTÃO DE CARTEIRA)
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Global</h2>", unsafe_allow_html=True)
    t_in = st.text_input("Ativo (Ex: BTC-USD, VULC3, TSLA):", value="BTC-USD").upper()
    is_crypto = "-" in t_in or len(t_in) > 6
    val_inv = st.number_input("Quanto investi (R$):", value=0.0)
    p_pago = st.number_input("Preço que paguei (R$):", value=0.0, format="%.2f")
    st.sidebar.button("🚀 Sincronizar Nexus")

# 4. MOTOR DE INTELIGÊNCIA INDEPENDENTE
t_f = t_in + ".SA" if not is_crypto and "." not in t_in and len(t_in) < 6 else t_in

try:
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    if not data.empty:
        p_at = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{t_in}</span></h1>", unsafe_allow_html=True)

        # PERFORMANCE
        c1, c2 = st.columns(2)
        lucro = (p_at - p_pago) * (val_inv / p_pago) if p_pago > 0 else 0
        c1.metric("Preço Agora", f"R$ {p_at:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {lucro:,.2f}", delta=f"{((p_at/p_pago)-1)*100:.2f}%" if p_pago > 0 else "0%")

        # VEREDITO DO ROBÔ (GRÁFICO + INTERNET)
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        tende = "ALTA" if p_at > data['Close'].mean() else "QUEDA"
        cor = "#00ff00" if tende == "ALTA" else "#ff4b4b"
        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor};'>
                <h4 style='color: {cor} !important;'>📢 RECOMENDAÇÃO: {tende}</h4>
                <p><b>Análise Master:</b> O ativo está em ciclo de {tende}. Suporte em R$ {data['Low'].tail(10).min():.2f}.</p>
                <p><b>Influência Mundial:</b> Fique atento aos EUA (S&P 500) no radar acima; se eles subirem, a tendência de {t_in} melhora.</p>
            </div>
        """, unsafe_allow_html=True)

        # GRÁFICO (RESTAURADO E VISÍVEL NO PC)
        st.markdown("<h4 class='neon-blue'>📈 Mapa de Preços</h4>", unsafe_allow_html=True)
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception: st.error("Sincronizando... Verifique a conexão do servidor.")
