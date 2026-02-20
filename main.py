import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Setup Visual "High Clarity" (Fundo Claro Inspirado no seu print)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #212529; }
    .stMetric { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-weight: 800; }
    .stInfo { background-color: #e7f3ff !important; color: #004085 !important; border-left: 5px solid #007bff !important; }
    .stSuccess { border-left: 5px solid #28a745 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Busca Inteligente (Causa Raiz Corrigida)
@st.cache_data(ttl=60)
def buscar_dados_v85(t, p="1d", i="1m"):
    try:
        # Identifica se é Cripto ou Global para evitar o erro de valor (R$ 29 vs US$ 67k)
        criptos = ["BTC", "XRP", "ETH", "SOL", "ADA", "DOGE"]
        globals = ["OHI", "AAPL", "MSFT", "JEPP34"]
        
        t_up = t.upper().strip()
        if t_up in criptos: search = f"{t_up}-USD"
        elif t_up in globals: search = t_up
        elif "-" in t_up or ".SA" in t_up: search = t_up
        else: search = f"{t_up}.SA"
            
        ticker = yf.Ticker(search)
        hist = ticker.history(period=p, interval=i)
        return hist, ticker.info
    except: return None, None

# 3. Motor de Mensagens
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ InvestSmart Control")
    token_bot = st.text_input("Token Telegram:", type="password")
    chat_id_user = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    # RADARES INDEPENDENTES (Não misturam as telas)
    if 'radar_p' not in st.session_state: st.session_state.radar_p = []
    if 'radar_s' not in st.session_state: st.session_state.radar_s = []
    
    modo = st.radio("Escolha o Terminal:", ["📈 Prateleira (Investidor)", "⚡ Swing Trade (Kandall)"])
    
    st.divider()
    st.subheader("➕ Adicionar Ativo")
    add_t = st.text_input("Ticker (Ex: PETR4, BTC, OHI):").upper().strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Adicionar"):
            if add_t:
                if modo == "📈 Prateleira (Investidor)":
                    if add_t not in st.session_state.radar_p: st.session_state.radar_p.append(add_t)
                else:
                    if add_t not in st.session_state.radar_s: st.session_state.radar_s.append(add_t)
                st.rerun()
    with col2:
        if st.button("Limpar Radar"):
            if modo == "📈 Prateleira (Investidor)": st.session_state.radar_p = []
            else: st.session_state.radar_s = []
            st.rerun()

# --- MODO 1: PRATELEIRA DE RENDA (FOCO EM LEIGOS) ---
if modo == "📈 Prateleira (Investidor)":
    st.title("🏛️ Prateleira de Monitoramento Estratégico")
    if not st.session_state.radar_p:
        st.info("👋 Radar limpo. Adicione ativos na barra lateral para ver o Veredito do Mentor.")
    else:
        for t in st.session_state.radar_p:
            h, info = buscar_dados_v85(t, "5d", "1h")
            if h is not None and not h.empty:
                atual = h['Close'].iloc[-1]
                moeda = "US$" if "-" in t or any(x in t.upper() for x in ["BTC", "XRP", "OHI"]) else "R$"
                dy = info.get('trailingAnnualDividendRate', 0)
                p_justo = (dy / 0.06) if dy > 0 else (atual * 1.15)
                
                with st.container():
                    c1, c2, c3 = st.columns([1, 1, 2])
                    c1.metric(f"💰 {t}", f"{moeda} {atual:,.2f}", f"{((atual/h.Open.iloc[0])-1)*100:.2f}%")
                    c2.metric("Preço Justo", f"{moeda} {p_justo:,.2f}")
                    with c3:
                        # Recuperando a Inteligência de Setor e Dividendos
                        txt_div = f"Paga R$ {dy:,.2f} de dividendos/ano." if dy > 0 else "Foco em valorização."
                        st.info(f"**Mentor:** Ativo sólido do setor de {info.get('sector', 'Global')}. {txt_div} Sugestão de venda em {moeda} {atual*1.20:,.2f} (+20%).")
                st.divider()

# --- MODO 2: SWING TRADE (FOCO EM GRÁFICO KANDALL) ---
else:
    st.title("⚡ Terminal Swing Trade | Análise Profissional")
    if not st.session_state.radar_s:
        st.info("👋 Adicione ativos específicos para análise de Trade na barra lateral.")
    else:
        t_sel = st.selectbox("Selecione o Ativo para Análise Técnica:", st.session_state.radar_s)
        h_t, i_t = buscar_dados_v85(t_sel, "60d", "1d")
        
        if h_t is not None and not h_t.empty:
            h_t['MA20'] = h_t['Close'].rolling(window=20).mean()
            h_t['MA9'] = h_t['Close'].rolling(window=9).mean()
            p_atual = h_t['Close'].iloc[-1]
            moeda = "US$" if "-" in t_sel or any(x in t_sel.upper() for x in ["BTC", "XRP", "OHI"]) else "R$"
            
            c_l, c_r = st.columns([1, 3])
            with c_l:
                st.metric(t_sel, f"{moeda} {p_atual:,.2f}")
                if h_t['MA9'].iloc[-1] > h_t['MA20'].iloc[-1]: 
                    st.success("🚀 SINAL: COMPRA")
                    enviar_alerta(token_bot, chat_id_user, f"🎯 GATILHO COMPRA: {t_sel} em {moeda}{p_atual}")
                else: st.error("⚠️ SINAL: AGUARDE")
                st.write(f"**Alvo Curto (5%):** {moeda} {p_atual*1.05:,.2f}")
            
            with c_r:
                # Gráfico Kendall (Candle) Recuperado
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
                fig.add_trace(go.Candlestick(x=h_t.index, open=h_t.Open, high=h_t.High, low=h_t.Low, close=h_t.Close, name='Kandall'), row=1, col=1)
                fig.add_trace(go.Scatter(x=h_t.index, y=h_t['MA20'], name='Tendência', line=dict(color='#28a745')), row=1, col=1)
                fig.update_layout(template='plotly_white', xaxis_rangeslider_visible=False, height=550, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

time.sleep(60)
st.rerun()
