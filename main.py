import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Layout (Garantindo que a fonte escura apareça no fundo claro)
st.set_page_config(page_title="InvestSmart Pro | Real Time", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #ffffff !important; }
    h1, h2, h3, p { color: #1a1a1a !important; }
    .stMetric { background-color: #f1f3f5 !important; border: 2px solid #dee2e6 !important; border-radius: 12px; padding: 20px; }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-size: 32px !important; }
    .stInfo { background-color: #e7f3ff !important; color: #004085 !important; border-left: 5px solid #007bff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Busca Blindado
def buscar_dados_v81(t):
    try:
        # Lógica para garantir que BTC, XRP e outros funcionem
        if t in ["BTC", "XRP", "ETH", "SOL"]:
            search = f"{t}-USD"
        elif "-" in t or ".SA" in t:
            search = t
        else:
            search = f"{t}.SA"
            
        ticker = yf.Ticker(search)
        # Busca 5 dias para ter certeza que tem histórico
        hist = ticker.history(period="5d", interval="5m")
        return hist, ticker.info
    except:
        return None, None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Painel de Controle")
    token = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    if 'radar' not in st.session_state:
        st.session_state.radar = ["BTC", "XRP", "BBAS3", "OHI"]
    
    add_item = st.text_input("Adicionar Ativo:").upper()
    if st.button("Adicionar") and add_item:
        if add_item not in st.session_state.radar:
            st.session_state.radar.append(add_item)
            st.rerun()
            
    if st.button("Limpar Tudo"):
        st.session_state.radar = []
        st.rerun()

# --- TERMINAL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Monitoramento em Tempo Real")

if not st.session_state.radar:
    st.info("Seu radar está vazio. Adicione ativos na barra lateral.")
else:
    # Mostra sempre os ativos em grupos de 2 por linha para não embolar
    for i in range(0, len(st.session_state.radar), 2):
        cols = st.columns(2)
        subset = st.session_state.radar[i:i+2]
        
        for idx, t in enumerate(subset):
            with cols[idx]:
                h, info = buscar_dados_v81(t)
                
                if h is not None and not h.empty:
                    atual = h['Close'].iloc[-1]
                    abertura = h['Open'].iloc[0]
                    var = ((atual/abertura)-1)*100
                    moeda = "US$" if "-" in t or t in ["BTC", "XRP", "ETH"] else "R$"
                    
                    st.metric(f"💰 {t}", f"{moeda} {atual:,.2f}", f"{var:.2f}%")
                    
                    # Informações do Mentor (Agora sempre visíveis)
                    setor = info.get('sector', 'Ativo Global')
                    dy = info.get('trailingAnnualDividendYield', 0) * 100
                    
                    st.info(f"**Mentor:** Este ativo de {setor} está operando {'em alta' if var > 0 else 'em queda'}. "
                            f"Rendimento de Dividendos: {dy:.2f}% ao ano.")
                    
                    # Mini Gráfico para não ficar em branco
                    fig = go.Figure(data=[go.Scatter(x=h.index, y=h['Close'], line=dict(color='#007bff', width=2))])
                    fig.update_layout(template='plotly_white', height=100, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False)
                    st.plotly_chart(fig, use_container_width=True, key=f"gr_{t}")
                else:
                    st.warning(f"Buscando dados de {t}... Verifique se o código está correto.")

# Atualização automática a cada 30 segundos
time.sleep(30)
st.rerun()
