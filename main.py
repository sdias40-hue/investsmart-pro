import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Layout High Clarity (Fundo Branco e Fontes Escuras)
st.set_page_config(page_title="InvestSmart Pro | Precision", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #ffffff; color: #212529; }
    .stMetric { background-color: #f8f9fa !important; border: 1px solid #dee2e6 !important; border-radius: 10px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-weight: bold; }
    .stInfo { background-color: #f0f7ff !important; color: #004085 !important; border: 1px solid #b8daff !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte Corrigidas
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

def buscar_dados_v80(t, p="1d", i="1m"):
    try:
        # Lógica de busca robusta para evitar erro de preço
        is_crypto = "-" in t or t in ["BTC", "ETH", "SOL", "XRP"]
        ticker_search = t if is_crypto or ".SA" in t else f"{t}.SA"
        ticker = yf.Ticker(ticker_search)
        hist = ticker.history(period=p, interval=i)
        return hist, ticker.info
    except: return None, None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Centro de Controle")
    token_bot = st.text_input("Token Telegram:", type="password")
    chat_id_user = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    modo = st.radio("Escolha o Terminal:", ["📈 Monitoramento (4 Ativos)", "⚡ Swing Trade (Kandall)"])
    
    st.divider()
    st.subheader("➕ Gerenciar Radar")
    if 'radar' not in st.session_state: st.session_state.radar = ["BTC-USD", "XRP-USD", "BBAS3", "OHI"]
    
    add_t = st.text_input("Novo Ativo (Ex: PETR4, AAPL):").upper()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Adicionar") and add_t:
            if add_t not in st.session_state.radar: st.session_state.radar.append(add_t)
    with col2:
        if st.button("Limpar Radar"): 
            st.session_state.radar = []
            st.rerun()

# --- MODO 1: MONITORAMENTO DE 4 PRODUTOS ---
if modo == "📈 Monitoramento (4 Ativos)":
    st.title("🏛️ Painel de Monitoramento Estratégico")
    if not st.session_state.radar:
        st.info("Adicione ativos para iniciar o monitoramento de 4 produtos.")
    else:
        # Exibe os primeiros 4 ativos do radar
        ativos_foco = st.session_state.radar[:4]
        cols = st.columns(2) # Grade 2x2
        
        for idx, t in enumerate(ativos_foco):
            with cols[idx % 2]:
                h, info = buscar_dados_v80(t, "1d", "5m")
                if h is not None and not h.empty:
                    atual = h['Close'].iloc[-1]
                    moeda = "US$" if "-" in t else "R$"
                    var = ((atual/h.Open.iloc[0])-1)*100
                    
                    st.metric(f"{t}", f"{moeda} {atual:,.2f}", f"{var:.2f}%")
                    
                    # Mentor Simplificado (image_d3cac0.jpg)
                    p_justo = (info.get('trailingAnnualDividendRate', 0) / 0.06) if info.get('trailingAnnualDividendRate') else (atual * 1.15)
                    st.write(f"🎯 **Preço Justo:** {moeda} {p_justo:,.2f}")
                    
                    status = "✅ OPORTUNIDADE" if atual < p_justo else "⏳ AGUARDE"
                    st.info(f"**Mentor:** {info.get('sector', 'Global')}. {status}")
                    
                    # Alerta Automático
                    if var > 2.0 or var < -2.0:
                        enviar_alerta(token_bot, chat_id_user, f"🚨 ALERTA: {t} com variação de {var:.2f}%!")

# --- MODO 2: SWING TRADE (KANDALL SEM ERROS) ---
else:
    st.title("⚡ Swing Trade | Alta Performance")
    if not st.session_state.radar:
        st.warning("Adicione ativos no radar lateral.")
    else:
        t_trade = st.selectbox("Selecione para Analisar:", st.session_state.radar)
        h_t, i_t = buscar_dados_v80(t_trade, "60d", "1d")
        
        if h_t is not None and not h_t.empty:
            h_t['MA20'] = h_t['Close'].rolling(window=20).mean()
            h_t['MA9'] = h_t['Close'].rolling(window=9).mean()
            p_atual = h_t['Close'].iloc[-1]
            
            c_l, c_r = st.columns([1, 3])
            with c_l:
                st.metric(t_trade, f"{p_atual:,.2f}")
                if h_t['MA9'].iloc[-1] > h_t['MA20'].iloc[-1]:
                    st.success("🚀 COMPRA CONFIRMADA")
                else: st.error("⚠️ AGUARDE SINAL")
                st.info(f"Analisando {t_trade}. Setor: {i_t.get('sector', 'Ativo Global')}")

            with c_r:
                # Gráfico Candle Corrigido (image_8a9b61.png)
                fig_v80 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
                fig_v80.add_trace(go.Candlestick(x=h_t.index, open=h_t.Open, high=h_t.High, low=h_t.Low, close=h_t.Close, name='Kandall'), row=1, col=1)
                fig_v80.add_trace(go.Scatter(x=h_t.index, y=h_t['MA20'], name='Média 20d', line=dict(color='#28a745')), row=1, col=1)
                fig_v80.update_layout(template='plotly_white', xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_v80, use_container_width=True)

    if st.button("🔄 Resetar Gráfico"): st.rerun()

time.sleep(30)
st.rerun()
