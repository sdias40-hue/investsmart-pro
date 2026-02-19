import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# 1. Configuração de Terminal Profissional
st.set_page_config(page_title="InvestSmart Pro | Home Broker", layout="wide")

# 2. Função de Alerta Telegram (O que faltava no outro chat)
def enviar_alerta_telegram(token, chat_id, mensagem):
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensagem}"
    requests.get(url)

# --- 3. MOTOR DE BUSCA EM TEMPO REAL (Foco em 1 Minuto) ---
def buscar_dados_tempo_real(t):
    try:
        for s in [f"{t}.SA", t]:
            ticker = yf.Ticker(s)
            # Intervalo de 1 minuto para visualização Home Broker
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty: return hist, ticker.info
        return None, None
    except: return None, None

# --- 4. INTERFACE ---
with st.sidebar:
    st.header("📊 Configuração Home Broker")
    ticker_final = st.text_input("Ticker Ativo:", "PETR4").upper()
    
    st.divider()
    st.header("🔔 Conectar Telegram")
    # Use o Token do seu Bot que aparece no seu print (BotFather)
    token_tg = st.text_input("Token do Bot:", type="password")
    id_tg = st.text_input("Seu ID (Chat ID):")
    
    if st.button("Testar Conexão"):
        enviar_alerta_telegram(token_tg, id_tg, f"🚀 Terminal InvestSmart conectado com sucesso para {ticker_final}!")
        st.success("Mensagem enviada!")

# --- 5. GRÁFICO DINÂMICO ---
if ticker_final:
    hist, info = buscar_dados_tempo_real(ticker_final)
    
    if hist is not None:
        # Indicadores de Trader (EMA 9 e Volume)
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        
        st.title(f"📈 Home Broker: {info.get('longName', ticker_final)}")
        
        # Alerta Automático de Rompimento
        if atual >= res:
            msg = f"⚠️ ALERTA: {ticker_final} rompeu a RESISTÊNCIA em {atual}!"
            enviar_alerta_telegram(token_tg, id_tg, msg)

        # Gráfico Home Broker (Igual ao image_8031d6.png)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='1 min'), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='Média Rápida', line=dict(color='#ffaa00')), row=1, col=1)
        
        # Volume (image_8031d6.png)
        fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume'), row=2, col=1)
        
        # Suporte e Resistência Dinâmicos
        fig.add_hline(y=res, line_dash="dot", line_color="red", row=1, col=1)
        fig.add_hline(y=sup, line_dash="dot", line_color="green", row=1, col=1)
        
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Mentor Inteligente (CONTEÚDO REAL)
        st.subheader("🤖 Análise do Mentor")
        st.info(f"Sandro, observe que no tempo gráfico de 1 minuto, o volume está {'ACIMA' if hist.Volume.iloc[-1] > hist.Volume.mean() else 'ABAIXO'} da média. "
                f"Isso indica que o movimento atual para buscar os {res} tem {'força' if hist.Volume.iloc[-1] > hist.Volume.mean() else 'fraqueza'}. "
                "Fique atento ao Telegram, o robô vai disparar se houver rompimento.")
