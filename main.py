import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Ultra Contraste (Fim das cores transparentes)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-weight: bold; }
    .stInfo { background-color: #0a0d12 !important; color: #ffffff !important; border: 1px solid #00ff88 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

def buscar_dados_v76(t, p="1d", i="1m"):
    try:
        t_s = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(t_s)
        hist = ticker.history(period=p, interval=i)
        return hist, ticker.info
    except: return None, None

# --- SIDEBAR: COMANDO CENTRAL ---
with st.sidebar:
    st.title("🛡️ Centro de Comando")
    token_bot = st.text_input("Token do Bot:", type="password")
    chat_id = st.text_input("Seu ID de Usuário (8392660003):")
    
    st.divider()
    modo = st.radio("Escolha o Modo de Operação:", ["🏛️ Prateleira de Renda", "⚡ Swing Trade (Especialista)"])
    
    st.divider()
    st.subheader("➕ Adicionar ao Radar")
    add_manual = st.text_input("Ticker Manual (Ex: VALE3):").upper()

# --- MODO 1: PRATELEIRA DE RENDA (ESTILO INVESTIDOR 10) ---
if modo == "🏛️ Prateleira de Renda":
    st.title("🏛️ Central de Renda e Dividendos")
    
    def exibir_categoria(titulo, lista):
        if lista:
            st.subheader(titulo)
            cols = st.columns(len(lista))
            for i, t in enumerate(lista):
                with cols[i]:
                    hist, info = buscar_dados_v76(t, "5d", "1h")
                    if hist is not None and not hist.empty:
                        atual = hist['Close'].iloc[-1]
                        dy = info.get('trailingAnnualDividendRate', 0)
                        st.metric(f"💰 {t}", f"R$ {atual:,.2f}")
                        st.caption(f"📅 Renda/Ano: R$ {dy:,.2f}")
                        st.info(f"**Análise:** {info.get('longName')} é do setor de {info.get('sector')}. Ativo sólido para renda.")
            st.divider()

    exibir_categoria("🪙 CRIPTOMOEDAS", ["BTC-USD", "ETH-USD"])
    exibir_categoria("🌎 INTERNACIONAL (BDR/ETF)", ["OHI", "JEPP34"])
    exibir_categoria("🇧🇷 AÇÕES BRASIL", ["BBAS3", "TAEE11"] + ([add_manual] if add_manual else []))

# --- MODO 2: SWING TRADE (ANÁLISE DE KENDALL) ---
else:
    st.title("⚡ Terminal Swing Trade | Estratégia Kandall")
    ticker_trade = add_manual if add_manual else st.selectbox("Selecione para Trade:", ["PETR4", "VULC3", "VALE3", "SOL-USD"])
    
    hist, info = buscar_dados_v76(ticker_trade, "60d", "1d")
    
    if hist is not None and not hist.empty:
        # Médias de Swing Trade (9 e 20 períodos)
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        atual = hist['Close'].iloc[-1]
        
        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric(ticker_trade, f"R$ {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            st.subheader("🤖 Mentor Trader")
            
            # Veredito Técnico
            if hist['MA9'].iloc[-1] > hist['MA20'].iloc[-1] and atual > hist['MA9'].iloc[-1]:
                st.success("🚀 GATILHO: Compra confirmada pelo cruzamento de médias.")
                enviar_alerta(token_bot, chat_id, f"🎯 COMPRA SWING: {ticker_trade} em {atual}")
            elif atual < hist['MA20'].iloc[-1]:
                st.error("⚠️ GATILHO: Venda/Alerta de Queda. Preço abaixo da tendência.")
            else:
                st.warning("⚖️ NEUTRO: Ativo em consolidação lateral.")

        with c2:
            # Gráfico de Candles (Kendall)
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Kandall'), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], name='Média 20d', line=dict(color='#00ff88')), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['MA9'], name='Média 9d', line=dict(color='#ffaa00')), row=1, col=1)
            
            cores_v = ['#00ff88' if hist.Close[i] >= hist.Open[i] else '#ff4b4b' for i in range(len(hist))]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=cores_v, name='Volume'), row=2, col=1)
            
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=600, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

    time.sleep(60)
    st.rerun()
