import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. VISIBILIDADE E QUALIDADE (PC E CELULAR)
st.set_page_config(page_title="Nexus Global | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, label, div { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Cards compactos para não perder qualidade no layout */
    .stMetric { 
        background-color: #0a0a0a !important; 
        border: 1px solid #333 !important; 
        border-radius: 12px; 
        padding: 15px;
    }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #ffffff !important; }
    
    /* Caixa de Veredito Profissional */
    .status-box { 
        background-color: #0e1117; 
        border-left: 8px solid #00d4ff; 
        padding: 20px; 
        border-radius: 10px; 
        margin: 15px 0;
        border: 1px solid #222;
    }
    
    /* Gráfico com borda e sombra */
    .stPlotlyChart { border: 1px solid #222; border-radius: 15px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 2. RADAR GLOBAL: BOLSAS DO MUNDO (TOP LAYOUT)
st.markdown("<h3 class='neon-blue'>🌍 Radar das Bolsas Mundiais</h3>", unsafe_allow_html=True)
indices = {"S&P 500 (EUA)": "^GSPC", "Nasdaq (Tech)": "^IXIC", "Ibovespa (BR)": "^BVSP"}
# Criamos 3 colunas para o topo não ficar esticado
c_top = st.columns(3)

for i, (nome, ticket) in enumerate(indices.items()):
    try:
        idx_data = yf.Ticker(ticket).history(period="2d")
        if len(idx_data) > 1:
            v_at = idx_data['Close'].iloc[-1]
            var = ((v_at / idx_data['Close'].iloc[-2]) - 1) * 100
            c_top[i].metric(nome, f"{v_at:,.0f}", f"{var:.2f}%")
    except: pass

# 3. GESTÃO E COMANDO LATERAL
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Global</h2>", unsafe_allow_html=True)
    t_in = st.text_input("Ativo (Ex: BTC-USD, VULC3):", value="BTC-USD").upper()
    val_inv = st.number_input("Valor Investido (R$):", value=0.0)
    p_pago = st.number_input("Preço de Entrada (R$):", value=0.0, format="%.2f")
    st.sidebar.button("🚀 Sincronizar Nexus")

# 4. MOTOR DE INTELIGÊNCIA 24H (SEM TRAVAMENTOS)
t_f = t_in + ".SA" if "-" not in t_in and "." not in t_in and len(t_in) < 6 else t_in

try:
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    if not data.empty:
        p_at = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{t_in}</span></h1>", unsafe_allow_html=True)

        # Performance do Ativo (2 colunas equilibradas)
        c1, c2 = st.columns(2)
        lucro = (p_at - p_pago) * (val_inv / p_pago) if p_pago > 0 else 0
        c1.metric("Preço Hoje", f"R$ {p_at:,.2f}")
        c2.metric("Meu Resultado", f"R$ {lucro:,.2f}", delta=f"{((p_at/p_pago)-1)*100:.2f}%" if p_pago > 0 else "0%")

        # VEREDITO MASTER DO ROBÔ
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        tende = "ALTA" if p_at > data['Close'].mean() else "QUEDA"
        cor = "#00ff00" if tende == "ALTA" else "#ff4b4b"
        
        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor};'>
                <h4 style='color: {cor} !important;'>📢 RECOMENDAÇÃO: {tende}</h4>
                <p>Suporte principal em R$ {data['Low'].tail(10).min():.2f}. Acompanhe o S&P 500 no radar acima para confirmar a força do movimento.</p>
            </div>
        """, unsafe_allow_html=True)

        # GRÁFICO MASTER (QUALIDADE DEFINITIVA)
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=10,r=10,t=10,b=10), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
except: st.error("Sincronizando com os mercados globais...")
