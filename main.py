import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. CSS de Ultra Contraste (Fim das cores transparentes)
st.set_page_config(page_title="InvestSmart Pro | Swing Trade", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stMetric { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-weight: bold; }
    .stInfo { background-color: #0a0d12 !important; color: #ffffff !important; border: 1px solid #00ff88 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Alerta Trader
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

# --- SIDEBAR: COMANDO DO TRADER ---
with st.sidebar:
    st.title("🛡️ Área do Trader")
    token_bot = st.text_input("Token Telegram:", type="password")
    chat_id = st.text_input("Seu ID:")
    
    st.divider()
    aba = st.tabs(["🏛️ Carteira Renda", "⚡ Swing Trade"])
    
    with aba[0]:
        st.write("Monitoramento de Longo Prazo")
        mon_renda = st.multiselect("Seus Ativos:", ["BBAS3", "TAEE11", "JEPP34", "OHI"], ["BBAS3", "OHI"])
    
    with aba[1]:
        st.write("🎯 Foco em Ganho de Capital")
        ticker_swing = st.text_input("Adicione Ação para Trade (Ex: VULC3, PETR4):", "VULC3").upper()

# --- ABA 2: MÓDULO SWING TRADE (O QUE VOCÊ PEDIU) ---
st.title(f"⚡ Painel Swing Trade: {ticker_swing}")

def buscar_dados_trade(t):
    try:
        t_s = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(t_s)
        # Swing trade usa gráfico Diário (Daily) para ver a tendência de dias
        hist = ticker.history(period="60d", interval="1d")
        return hist, ticker.info
    except: return None, None

hist, info = buscar_dados_trade(ticker_swing)

if hist is not None and not hist.empty:
    # --- INDICADORES DE TRADER PROFISSIONAL ---
    hist['MA20'] = hist['Close'].rolling(window=20).mean() # Média de 20 dias (Tendência)
    hist['MA9'] = hist['Close'].rolling(window=9).mean()   # Média de 9 dias (Gatilho)
    atual = hist['Close'].iloc[-1]
    anterior = hist['Close'].iloc[-2]
    vol_atual = hist['Volume'].iloc[-1]
    vol_medio = hist['Volume'].mean()

    c1, c2 = st.columns([1, 3])
    
    with c1:
        st.metric("Preço de Tela", f"R$ {atual:,.2f}", f"{((atual/anterior)-1)*100:.2f}%")
        
        st.subheader("🤖 Mentor Swing Trader")
        
        # --- LÓGICA DE ALERTA DE COMPRA/VENDA (GATILHO) ---
        if hist['MA9'].iloc[-1] > hist['MA20'].iloc[-1] and atual > hist['MA9'].iloc[-1]:
            status = "🚀 COMPRA (Tendência de Alta Confirmada)"
            conselho = "As médias cruzaram para cima. Volume está saudável. É um bom momento para buscar lucro nos próximos dias."
            st.success(status)
            enviar_alerta(token_bot, chat_id, f"🎯 GATILHO SWING TRADE: Compra em {ticker_swing} a {atual}")
        elif atual < hist['MA20'].iloc[-1]:
            status = "⚠️ VENDA / AGUARDE (Tendência de Baixa)"
            conselho = "O preço perdeu a média de 20 dias. Risco de queda continuada. Proteja seu capital."
            st.error(status)
        else:
            status = "⚖️ NEUTRO (Lateralização)"
            conselho = "O ativo está "andando de lado". Sem gatilho claro de entrada agora."
            st.warning(status)
            
        st.info(f"**Análise Setorial:** {info.get('longName')} atua no setor de {info.get('sector')}. {conselho}")
        
        st.divider()
        st.write(f"📈 **Suporte:** R$ {hist['Low'].tail(10).min():,.2f}")
        st.write(f"📉 **Resistência:** R$ {hist['High'].tail(10).max():,.2f}")

    with c2:
        # --- GRÁFICO KANDALL (CANDLESTICKS) DE ALTA DEFINIÇÃO ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
        
        # Velas (Candles)
        fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Candle'), row=1, col=1)
        
        # Médias Móveis (Linhas de Tendência)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], name='Média 20d (Tendência)', line=dict(color='#00ff88', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['MA9'], name='Média 9d (Gatilho)', line=dict(color='#ffaa00', width=1.5)), row=1, col=1)
        
        # Volume Colorido (Verde/Vermelho)
        cores_v = ['#00ff88' if hist.Close[i] >= hist.Open[i] else '#ff4b4b' for i in range(len(hist))]
        fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=cores_v, name='Volume'), row=2, col=1)
        
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=650, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    time.sleep(60)
    st.rerun()
