import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Visibilidade Master (PC e Celular)
st.set_page_config(page_title="Nexus Global | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, label, div { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important;
    }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Card de métricas responsivo */
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #ffffff !important; }
    .stMetric { 
        background-color: #0a0a0a !important; 
        border: 1px solid #00d4ff !important; 
        border-radius: 10px; 
        padding: 10px;
    }
    
    /* Caixa de Veredito que se adapta */
    .status-box { 
        background-color: #0e1117; 
        border-left: 8px solid #00d4ff; 
        padding: 15px; 
        border-radius: 8px; 
        margin: 10px 0;
    }
    
    /* Forçar gráfico a ser visível mas flexível */
    .stPlotlyChart { min-height: 400px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Radar Global (Indices Mundiais)
st.markdown("<h3 class='neon-blue'>🌍 Radar das Bolsas Mundiais</h3>", unsafe_allow_html=True)
indices = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Ibovespa": "^BVSP"}
# Colunas que se empilham sozinhas no celular
c_idx = st.columns(len(indices))

for i, (nome, ticket) in enumerate(indices.items()):
    try:
        idx_data = yf.Ticker(ticket).history(period="2d")
        if len(idx_data) > 1:
            v_at = idx_data['Close'].iloc[-1]
            var = ((v_at / idx_data['Close'].iloc[-2]) - 1) * 100
            c_idx[i].metric(nome, f"{v_at:,.0f}", f"{var:.2f}%")
    except: pass

# 3. Inteligência e Gestão do Ativo
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Command</h2>", unsafe_allow_html=True)
    t_in = st.text_input("Ativo (Ex: BTC-USD, VULC3, JEPQ34):", value="BTC-USD").upper()
    val_inv = st.number_input("Valor Investido (R$):", value=0.0)
    p_pago = st.number_input("Preço de Entrada (R$):", value=0.0, format="%.2f")
    st.sidebar.button("🚀 Gerar Inteligência")

t_f = t_in + ".SA" if "-" not in t_in and "." not in t_in and len(t_in) < 6 else t_in

try:
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    if not data.empty:
        p_at = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{t_in}</span></h1>", unsafe_allow_html=True)

        # Performance do Investimento
        c1, c2 = st.columns(2)
        lucro = (p_at - p_pago) * (val_inv / p_pago) if p_pago > 0 else 0
        c1.metric("Preço Hoje", f"R$ {p_at:,.2f}")
        c2.metric("Meu Resultado", f"R$ {lucro:,.2f}", delta=f"{((p_at/p_pago)-1)*100:.2f}%" if p_pago > 0 else "0%")

        # Veredito do Robô (Lógica Server-Side)
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        tende = "ALTA" if p_at > data['Close'].mean() else "QUEDA"
        cor = "#00ff00" if tende == "ALTA" else "#ff4b4b"
        
        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor};'>
                <h4 style='color: {cor} !important;'>📢 RECOMENDAÇÃO: {tende}</h4>
                <p>Suporte principal em R$ {data['Low'].tail(10).min():.2f}. A tendência global influencia {t_in}.</p>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico Master (Responsivo)
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
except: st.error("Sincronizando com os mercados mundiais...")
