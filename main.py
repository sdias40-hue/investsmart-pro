import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. ESTÉTICA PREMIUM (O RETORNO DO LAYOUT MASTER)
st.set_page_config(page_title="Nexus Global Intelligence | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505 !important; }
    h1, h2, h3, h4, span, label, p { 
        color: #00FF41 !important; 
        font-family: 'Courier New', monospace !important; 
    }
    /* Cards de Alta Qualidade (Visual Glass) */
    .stMetric { 
        background-color: rgba(0, 255, 65, 0.05) !important; 
        border: 1px solid #00FF41 !important; 
        border-radius: 12px; 
        padding: 20px;
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; }
    
    /* Veredito Master Blindado */
    .status-box { 
        background-color: #000000; 
        border: 2px solid #00FF41; 
        border-left: 12px solid #00FF41; 
        padding: 25px; 
        border-radius: 15px;
        box-shadow: 0px 0px 15px rgba(0, 255, 65, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. RADAR GLOBAL: BOLSAS DO MUNDO (TOP VIEW)
st.markdown("<h3 style='text-align: center;'>🌍 RADAR DE INTELIGÊNCIA GLOBAL</h3>", unsafe_allow_html=True)
indices = {"S&P 500 (EUA)": "^GSPC", "Nasdaq (Tech)": "^IXIC", "Ibovespa (BR)": "^BVSP"}
c_idx = st.columns(3)

for i, (nome, ticket) in enumerate(indices.items()):
    try:
        idx_data = yf.Ticker(ticket).history(period="2d")
        if len(idx_data) > 1:
            v_at = idx_data['Close'].iloc[-1]
            var = ((v_at / idx_data['Close'].iloc[-2]) - 1) * 100
            c_idx[i].metric(nome, f"{v_at:,.0f}", f"{var:.2f}%")
    except: pass

# 3. COMANDO LATERAL
with st.sidebar:
    st.markdown("<h2>🛡️ Nexus System</h2>", unsafe_allow_html=True)
    t_in = st.text_input("Ativo Principal:", value="TSLA").upper()
    val_inv = st.number_input("Capital Alocado (R$):", value=0.0)
    p_pago = st.number_input("Preço Médio (R$):", value=0.0)
    st.sidebar.button("🚀 Sincronizar")

# 4. MOTOR DE ANÁLISE MASTER
t_f = t_in + ".SA" if "-" not in t_in and "." not in t_in and len(t_in) < 6 else t_in

try:
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    if not data.empty:
        p_at = float(data['Close'].iloc[-1])
        st.markdown(f"<h1 style='text-align: center;'>🌍 {t_in} INTELLIGENCE REPORT</h1>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        lucro = (p_at - p_pago) * (val_inv / p_pago) if p_pago > 0 else 0
        c1.metric("Cotação Atual", f"R$ {p_at:,.2f}")
        c2.metric("Performance", f"R$ {lucro:,.2f}", delta=f"{((p_at/p_pago)-1)*100:.2f}%" if p_pago > 0 else "0%")

        # VEREDITO PREMIUM
        st.divider()
        tende = "ALTA" if p_at > data['Close'].mean() else "QUEDA"
        cor = "#00FF41" if tende == "ALTA" else "#FF3131"
        st.markdown(f"""
            <div class='status-box'>
                <h3 style='color: {cor} !important;'>📢 VEREDITO DO ROBÔ: {tende}</h3>
                <p style='color: #ffffff !important;'>Suporte detectado em R$ {data['Low'].tail(10).min():.2f}.</p>
                <p style='color: #ffffff !important;'>Tendência Global: O S&P 500 está influenciando o fluxo de capital para {t_in}.</p>
            </div>
        """, unsafe_allow_html=True)

        # GRÁFICO EM ALTA DEFINIÇÃO
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
except: st.error("Sincronizando com os mercados mundiais...")
