import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Layout High Clarity (Inspirado no image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #212529; }
    .stMetric { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-weight: 800; }
    .stInfo { background-color: #e7f3ff !important; color: #004085 !important; border-left: 5px solid #007bff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte Blindadas
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=60)
def buscar_dados_v82(t, p="1d", i="1m"):
    try:
        # Lógica para garantir BTC, XRP e BDRs funcionem (image_e1717f.jpg)
        if t in ["BTC", "XRP", "ETH"]: search = f"{t}-USD"
        elif "-" in t or ".SA" in t: search = t
        else: search = f"{t}.SA"
            
        ticker = yf.Ticker(search)
        hist = ticker.history(period=p, interval=i)
        return hist, ticker.info
    except: return None, None

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ InvestSmart Control")
    token_bot = st.text_input("Token Telegram:", type="password")
    chat_id_user = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    modo = st.radio("Escolha o Terminal:", ["📈 Prateleira de Renda", "⚡ Swing Trade (Kandall)"])
    
    st.divider()
    st.subheader("➕ Gerenciar Radar")
    if 'radar' not in st.session_state: st.session_state.radar = ["BTC", "XRP", "BBAS3", "OHI"]
    
    add_t = st.text_input("Novo Ativo:").upper()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Adicionar") and add_t:
            if add_t not in st.session_state.radar: 
                st.session_state.radar.append(add_t)
                enviar_alerta(token_bot, chat_id_user, f"✅ Monitorando: {add_t}")
                st.rerun()
    with col2:
        if st.button("Limpar Tudo"): 
            st.session_state.radar = []
            st.rerun()

# --- TERMINAL 1: PRATELEIRA DE RENDA (image_df2bc5.jpg) ---
if modo == "📈 Prateleira de Renda":
    st.title("🏛️ Prateleira de Investimentos Sólidos")
    if not st.session_state.radar:
        st.info("Radar vazio. Adicione ativos na barra lateral.")
    else:
        for t in st.session_state.radar:
            h, info = buscar_dados_v82(t, "5d", "1h")
            if h is not None and not h.empty:
                atual = h['Close'].iloc[-1]
                dy = info.get('trailingAnnualDividendRate', 0)
                p_justo = (dy / 0.06) if dy > 0 else (atual * 1.12)
                
                with st.container():
                    c1, c2, c3 = st.columns([1, 1, 2])
                    c1.metric(f"💰 {t}", f"{atual:,.2f}")
                    c2.metric("Preço Justo", f"{p_justo:,.2f}")
                    with c3:
                        st.info(f"**Mentor:** Ativo de {info.get('sector', 'Global')}. Sugestão de venda em R$ {atual*1.20:,.2f} (+20%).")
                        if dy > 0: st.success(f"💎 Pagadora de Dividendos: R$ {dy:,.2f}/ano")
                st.divider()

# --- TERMINAL 2: SWING TRADE (image_8aad4d.png) ---
else:
    st.title("⚡ Terminal Swing Trade | Tempo Real")
    if not st.session_state.radar:
        st.warning("Adicione ativos no radar lateral.")
    else:
        t_sel = st.selectbox("Ativo para Analisar:", st.session_state.radar)
        h_t, i_t = buscar_dados_v82(t_sel, "60d", "1d")
        
        if h_t is not None and not h_t.empty:
            h_t['MA20'] = h_t['Close'].rolling(window=20).mean()
            h_t['MA9'] = h_t['Close'].rolling(window=9).mean()
            p_atual = h_t['Close'].iloc[-1]
            
            c_l, c_r = st.columns([1, 3])
            with c_l:
                st.metric(t_sel, f"{p_atual:,.2f}")
                if h_t['MA9'].iloc[-1] > h_t['MA20'].iloc[-1]: st.success("🚀 COMPRA")
                else: st.error("⚠️ AGUARDE")
                st.write(f"**Setor:** {i_t.get('sector', 'Global')}")

            with c_r:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
                fig.add_trace(go.Candlestick(x=h_t.index, open=h_t.Open, high=h_t.High, low=h_t.Low, close=h_t.Close, name='Candle'), row=1, col=1)
                fig.add_trace(go.Scatter(x=h_t.index, y=h_t['MA20'], name='Tendência', line=dict(color='#28a745')), row=1, col=1)
                fig.update_layout(template='plotly_white', xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
