import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. FORÇAR LAYOUT ESCURO E VISIBILIDADE (Resolve fundo branco/letras sumidas)
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Forçar Fundo Preto Absoluto em tudo */
    .stApp, .main, header, .stSidebar, [data-testid="stHeader"] { 
        background-color: #000000 !important; 
    }
    
    /* Forçar Letras Brancas para leitura nítida */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important; 
    }
    
    /* AJUSTE DA SETA: Pequena aba azul discreta no celular */
    [data-testid="collapsedControl"] {
        background-color: #00d4ff !important;
        border-radius: 0 10px 10px 0;
        width: 35px !important;
        height: 35px !important;
        top: 10px !important;
    }
    /* Seta real no lugar do texto 'keyboard_double' */
    [data-testid="collapsedControl"]::before {
        content: "〉" !important;
        color: #000000 !important;
        font-weight: bold;
        position: absolute;
        left: 10px;
        top: 4px;
        font-size: 18px;
    }
    [data-testid="collapsedControl"] span { display: none !important; }

    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Cards de Métricas e Mentor */
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; }
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. MENU LATERAL (Aba de Comandos)
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    t_in = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Gestão</h4>", unsafe_allow_html=True)
    v_inv = st.number_input("Valor investido (R$):", value=0.0)
    p_pago = st.number_input("Preço pago:", value=0.0, format="%.2f")
    if st.sidebar.button("🚀 Sincronizar Tudo"):
        st.rerun()

# 3. EXIBIÇÃO DO DASHBOARD (Motor Blindado contra Erros)
t_f = t_in + ".SA" if len(t_in) < 6 and "." not in t_in else t_in

try:
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    if not data.empty:
        p_at = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{t_in}</span></h1>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        lucro = (p_at - p_pago) * (v_inv / p_pago) if p_pago > 0 else 0
        c1.metric("Preço Hoje", f"R$ {p_at:,.2f}")
        c2.metric("Meu Lucro", f"R$ {lucro:,.2f}", delta=f"{((
