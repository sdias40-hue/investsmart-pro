import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Layout "High Clarity" (Inspirado no image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Clarity", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #212529; }
    .stMetric { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-weight: 800; }
    .stInfo { background-color: #e7f3ff !important; color: #004085 !important; border: 1px solid #b8daff !important; border-radius: 8px; }
    .stSuccess { background-color: #d4edda !important; color: #155724 !important; }
    .stError { background-color: #f8d7da !important; color: #721c24 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

def buscar_dados_v78(t, p="1d", i="1m"):
    try:
        # Busca inteligente para BDRs, Criptos e Ações
        ticker_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(ticker_search)
        hist = ticker.history(period=p, interval=i)
        if hist.empty:
            ticker = yf.Ticker(t)
            hist = ticker.history(period=p, interval=i)
        return hist, ticker.info
    except: return None, None

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ InvestSmart Control")
    token_bot = st.text_input("Token do Bot (Telegram):", type="password")
    chat_id_user = st.text_input("Seu ID (Chat ID):", value="8392660003")
    
    st.divider()
    modo_terminal = st.radio("Selecione o Terminal:", ["🏛️ Prateleira de Renda", "⚡ Swing Trade (Kandall)"])
    
    st.divider()
    st.subheader("➕ Gerenciar Meu Radar")
    add_ticker = st.text_input("Adicionar Ativo (Ex: PETR4, OHI, BTC-USD):").upper()
    
    if 'radar' not in st.session_state: st.session_state.radar = []
        
    col_bt1, col_bt2 = st.columns(2)
    with col_bt1:
        if st.button("Adicionar") and add_ticker:
            if add_ticker not in st.session_state.radar:
                st.session_state.radar.append(add_ticker)
                st.success(f"{add_ticker} OK!")
    with col_bt2:
        if st.button("Limpar Radar"):
            st.session_state.radar = []
            st.rerun()

# --- TERMINAL 1: PRATELEIRA DE RENDA ---
if modo_terminal == "🏛️ Prateleira de Renda":
    st.title("🏛️ Sua Prateleira de Renda Personalizada")
    if not st.session_state.radar:
        st.info("👋 Radar vazio. Adicione ativos na barra lateral para começar.")
    else:
        grid = st.columns(3)
        for idx, t_radar in enumerate(st.session_state.radar):
            with grid[idx % 3]:
                h, info = buscar_dados_v78(t_radar, "5d", "1h")
                if h is not None:
                    preco = h['Close'].iloc[-1]
                    dy_v = info.get('trailingAnnualDividendRate', 0)
                    st.metric(f"💰 {t_radar}", f"R$ {preco:,.2f}", f"{((preco/h.Open.iloc[0])-1)*100:.2f}%")
                    
                    # Mentor Renda Especializado
                    txt_dy = f"Excelente! Paga R$ {dy_v:,.2f} de dividendos/ano." if dy_v > 0 else "Foco em valorização (Growth)."
                    st.info(f"**Mentor:** {info.get('longName')} no setor {info.get('sector')}. {txt_dy}")
                else: st.error(f"Erro em {t_radar}")

# --- TERMINAL 2: SWING TRADE ---
else:
    st.title("⚡ Terminal Swing Trade | Análise Profissional")
    if not st.session_state.radar:
        st.info("👋 Adicione ativos no radar lateral para abrir o gráfico.")
    else:
        t_trade = st.selectbox("Escolha o Ativo para Analisar:", st.session_state.radar)
        h_t, i_t = buscar_dados_v78(t_trade, "60d", "1d")
        
        if h_t is not None:
            # Indicadores e Médias
            h_t['MA20'] = h_t['Close'].rolling(window=20).mean()
            h_t['MA9'] = h_t['Close'].rolling(window=9).mean()
            p_atual = h_t['Close'].iloc[-1]
            
            c_left, c_right = st.columns([1, 3])
            with c_left:
                st.metric(t_trade, f"R$ {p_atual:,.2f}")
                st.subheader("🤖 Mentor Trader")
                
                # Inteligência de Dividendos no Trade
                dy_t = i_t.get('trailingAnnualDividendRate', 0)
                if dy_t > 0: st.success(f"💎 Ativo Dividend Payback: R$ {dy_t:,.2f}/ano")
                
                if h_t['MA9'].iloc[-1] > h_t['MA20'].iloc[-1]:
                    st.success("🚀 GATILHO COMPRA!")
                    enviar_alerta(token_bot, chat_id_user, f"🎯 COMPRA: {t_trade} em {p_atual}")
                else: st.error("⚠️ AGUARDE SINAL")
                st.info(f"Analisando {t_trade}. Setor: {i_t.get('sector', 'Global')}.")

            with c_right:
                # Gráfico Kendall (Candle)                 fig_t = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
                fig_t.add_trace(go.Candlestick(x=h_t.index, open=h_t.Open, high=h_t.High, low=h_t.Low, close=h_t.Close, name='Kendall'), row=1, col=1)
                fig_t.add_trace(go.Scatter(x=h_t.index, y=h_t['MA20'], name='Tendência', line=dict(color='#28a745')), row=1, col=1)
                fig_t.add_trace(go.Scatter(x=h_t.index, y=h_t['MA9'], name='Gatilho', line=dict(color='#ffc107')), row=1, col=1)
                
                v_cols = ['#28a745' if h_t.Close[i] >= h_t.Open[i] else '#dc3545' for i in range(len(h_t))]
                fig_t.add_trace(go.Bar(x=h_t.index, y=h_t['Volume'], marker_color=v_cols, name='Volume'), row=2, col=1)
                
                fig_t.update_layout(template='plotly_white', xaxis_rangeslider_visible=False, height=600, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_t, use_container_width=True)

    time.sleep(30)
    st.rerun()
