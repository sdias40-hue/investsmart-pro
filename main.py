import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Setup Visual de Alta Clareza (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #212529; }
    .stMetric { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-weight: 800; }
    .stInfo { background-color: #e7f3ff !important; color: #004085 !important; border-left: 5px solid #007bff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Busca e Mensageria Corrigido
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=60)
def buscar_dados_v84(t, p="1d", i="1m"):
    try:
        # Lógica para garantir valores reais (BTC, XRP e BDRs)
        is_global = t.upper() in ["BTC", "XRP", "ETH", "SOL", "OHI", "AAPL", "AAPL34"]
        search = f"{t.upper()}-USD" if is_global and "-" not in t else (t if ".SA" in t or "-" in t else f"{t}.SA")
        
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
    # Inicia os Radares vazios para total independência
    if 'radar_prateleira' not in st.session_state: st.session_state.radar_prateleira = []
    if 'radar_swing' not in st.session_state: st.session_state.radar_swing = []
    
    modo = st.radio("Selecione o Terminal:", ["📈 Monitorar Prateleira", "⚡ Swing Trade (Kandall)"])
    
    st.divider()
    st.subheader("➕ Adicionar ao Radar")
    add_t = st.text_input("Ticker (Ex: PETR4, BTC, OHI):").upper()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Adicionar"):
            if add_t:
                if modo == "📈 Monitorar Prateleira":
                    st.session_state.radar_prateleira.append(add_t)
                else:
                    st.session_state.radar_swing.append(add_t)
                enviar_alerta(token_bot, chat_id_user, f"✅ Monitorando {add_t} no {modo}")
                st.rerun()
    with col2:
        if st.button("Limpar Radar"):
            if modo == "📈 Monitorar Prateleira": st.session_state.radar_prateleira = []
            else: st.session_state.radar_swing = []
            st.rerun()

# --- MODO 1: MONITORAMENTO (PRATELEIRA) ---
if modo == "📈 Monitorar Prateleira":
    st.title("🏛️ Prateleira de Monitoramento Estratégico")
    if not st.session_state.radar_prateleira:
        st.info("👋 Radar limpo. Adicione até 4 ativos na barra lateral para começar.")
    else:
        grid = st.columns(2)
        for idx, t in enumerate(st.session_state.radar_prateleira[:4]):
            with grid[idx % 2]:
                h, info = buscar_dados_v84(t, "5d", "1h")
                if h is not None and not h.empty:
                    atual = h['Close'].iloc[-1]
                    moeda = "US$" if "-" in h.index.name or any(x in t for x in ["BTC", "XRP", "OHI"]) else "R$"
                    dy = info.get('trailingAnnualDividendRate', 0)
                    p_justo = (dy / 0.06) if dy > 0 else (atual * 1.15)
                    
                    st.metric(f"💰 {t}", f"{moeda} {atual:,.2f}", f"{((atual/h.Open.iloc[0])-1)*100:.2f}%")
                    st.write(f"🎯 **Preço Justo:** {moeda} {p_justo:,.2f}")
                    st.info(f"**Mentor:** {info.get('longName')} no setor {info.get('sector')}. {'Foco em Dividendos.' if dy > 0 else 'Foco em Crescimento.'}")
                else: st.warning(f"Buscando dados de {t}...")

# --- MODO 2: SWING TRADE (INDEPENDENTE) ---
else:
    st.title("⚡ Terminal Swing Trade | Análise Profissional")
    if not st.session_state.radar_swing:
        st.info("👋 Adicione ativos específicos para Swing Trade na barra lateral.")
    else:
        t_sel = st.selectbox("Escolha o Ativo para Analisar:", st.session_state.radar_swing)
        h_t, i_t = buscar_dados_v84(t_sel, "60d", "1d")
        
        if h_t is not None and not h_t.empty:
            h_t['MA20'] = h_t['Close'].rolling(window=20).mean()
            h_t['MA9'] = h_t['Close'].rolling(window=9).mean()
            p_atual = h_t['Close'].iloc[-1]
            
            c_l, c_r = st.columns([1, 3])
            with c_l:
                st.metric(t_sel, f"{p_atual:,.2f}")
                if h_t['MA9'].iloc[-1] > h_t['MA20'].iloc[-1]: st.success("🚀 SINAL: COMPRA")
                else: st.error("⚠️ SINAL: AGUARDE")
                st.info(f"Analisando {t_sel}. Setor: {i_t.get('sector', 'Global')}")

            with c_r:
                # Gráfico Candle Real Time
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
                fig.add_trace(go.Candlestick(x=h_t.index, open=h_t.Open, high=h_t.High, low=h_t.Low, close=h_t.Close, name='Candle'), row=1, col=1)
                fig.add_trace(go.Scatter(x=h_t.index, y=h_t['MA20'], name='Tendência', line=dict(color='#28a745')), row=1, col=1)
                fig.update_layout(template='plotly_white', xaxis_rangeslider_visible=False, height=550, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

time.sleep(60)
st.rerun()
