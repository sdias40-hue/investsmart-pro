import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Visibilidade (PC e Celular)
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Forçar Fundo Preto e Letras Brancas Master */
    .stApp, .main, header, .stSidebar, [data-testid="stHeader"] { 
        background-color: #000000 !important; 
    }
    h1, h2, h3, h4, p, span, label, div { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important; 
    }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }

    /* Aba azul discreta no celular para o menu lateral */
    [data-testid="collapsedControl"] {
        background-color: #00d4ff !important;
        border-radius: 0 12px 12px 0;
        width: 40px !important;
        height: 40px !important;
        top: 15px !important;
        left: 0 !important;
    }
    [data-testid="collapsedControl"]::before {
        content: "〉" !important;
        color: #000000 !important;
        font-size: 20px !important;
        font-weight: bold;
        position: absolute;
        left: 12px;
        top: 6px;
    }
    [data-testid="collapsedControl"] span { display: none !important; }

    /* Cards e Caixas do Mentor */
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; }
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Gestão de Ativos
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Dados da Carteira</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor total investido (R$):", value=0.0)
    preco_pago = st.number_input("Preço que paguei:", value=0.0, format="%.2f")
    
    if st.sidebar.button("🚀 Sincronizar Tudo"):
        st.rerun()

# 3. Motor de Busca e Exibição (Blindado)
ticker_f = ticker_input + ".SA" if len(ticker_input) < 6 and "." not in ticker_input else ticker_input

try:
    data = yf.download(ticker_f, period="60d", interval="1d", progress=False)
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # Performance Calculada com Segurança
        c1, c2 = st.columns(2)
        lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        variacao = ((p_atual / preco_pago) - 1) * 100 if preco_pago > 0 else 0
        
        c1.metric("Preço Hoje", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro", f"R$ {lucro_r:,.2f}", delta=f"{variacao:.2f}%")

        st.divider()
        st.markdown("<h3 class='neon-blue'>💡 O que o robô recomenda agora?</h3>", unsafe_allow_html=True)
        
        topo_10 = float(data['High'].tail(10).max())
        fundo_10 = float(data['Low'].tail(10).min())
        
        col_c, col_v = st.columns(2)
        with col_c:
            st.markdown(f"<div class='mentor-box'><h4>🛒 Comprar perto de:</h4><p class='neon-blue'>R$ {fundo_10:.2f}</p></div>", unsafe_allow_html=True)
        with col_v:
            st.markdown(f"<div class='mentor-box'><h4>💰 Vender perto de:</h4><p class='neon-blue'>R$ {topo_10:.2f}</p></div>", unsafe_allow_html=True)

        # Gráfico Master (Sempre visível no PC)
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception:
    st.error("Sincronizando... Verifique o código do ativo.")
