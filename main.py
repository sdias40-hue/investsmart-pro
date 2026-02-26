import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. FORÇAR LAYOUT ESCURO (Correção de Contraste Sandro)
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Forçar Fundo Preto em tudo para as letras brancas aparecerem */
    .stApp, .main, header, .stSidebar, [data-testid="stHeader"] { 
        background-color: #000000 !important; 
    }
    
    /* Forçar Letras Brancas em tudo */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important; 
    }
    
    /* Cor destaque Neon Blue */
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Cards de Métricas com Borda */
    .stMetric { 
        background-color: #0a0a0a !important; 
        border: 1px solid #00d4ff !important; 
        border-radius: 8px; 
    }
    
    /* AJUSTE CRÍTICO: Seta do menu lateral branca para fundo preto */
    button[kind="header"] {
        color: #ffffff !important;
    }
    
    /* Caixas do Mentor */
    .mentor-box { 
        background-color: #0e1117; 
        border-left: 6px solid #00d4ff; 
        padding: 20px; 
        border-radius: 8px; 
        border: 1px solid #333; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MENU LATERAL (Gerenciamento de Ativos)
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Gestão</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor investido (R$):", value=0.0)
    preco_pago = st.number_input("Preço pago:", value=0.0, format="%.2f")
    
    if st.sidebar.button("🚀 Sincronizar Tudo"):
        st.rerun()

# 3. EXIBIÇÃO DO DASHBOARD
ticker_f = ticker_input + ".SA" if len(ticker_input) < 6 and "." not in ticker_input else ticker_input

try:
    data = yf.download(ticker_f, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # Cotação e Lucro
        c1, c2 = st.columns(2)
        lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        c1.metric("Preço Hoje", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro", f"R$ {lucro_r:,.2f}", delta=f"{((p_atual/preco_pago)-1)*100 if preco_pago > 0 else 0:.2f}%")

        # Orientações do Mentor
        st.divider()
        topo_10 = float(data['High'].tail(10).max())
        fundo_10 = float(data['Low'].tail(10).min())
        
        col_c, col_v = st.columns(2)
        with col_c:
            st.markdown(f"<div class='mentor-box'><h4>🛒 Comprar perto de:</h4><p class='neon-blue'>R$ {fundo_10:.2f}</p></div>", unsafe_allow_html=True)
        with col_v:
            st.markdown(f"<div class='mentor-box'><h4>💰 Vender perto de:</h4><p class='neon-blue'>R$ {topo_10:.2f}</p></div>", unsafe_allow_html=True)

        # Gráfico Master (Sempre visível no PC)
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='black', plot_bgcolor='black', margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

except:
    st.error("Aguardando código do ativo...")
