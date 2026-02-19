import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração do Terminal
st.set_page_config(page_title="InvestSmart Pro | Home Broker", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# --- 2. MOTOR DE COMUNICAÇÃO (TELEGRAM) ---
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            # Rota oficial da API do Telegram
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": mensagem}
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            return str(e)
    return None

# --- 3. MOTOR DE BUSCA (MODO 1 MINUTO) ---
def buscar_dados_hb(t):
    try:
        # Tenta com sufixo .SA (Brasil) ou direto (EUA/Cripto)
        ticker_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(ticker_search)
        # 1d com intervalo de 1m para efeito de Home Broker
        hist = ticker.history(period="1d", interval="1m")
        if hist.empty:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="1d", interval="1m")
        return hist, ticker.info
    except:
        return None, None

# --- 4. INTERFACE LATERAL (RADAR) ---
with st.sidebar:
    st.header("📊 Home Broker Setup")
    ticker_input = st.text_input("Ativo Principal (Ex: PETR4, BTC-USD):", "PETR4").upper()
    
    st.divider()
    st.header("🔔 Conexão Telegram")
    token_tg = st.text_input("Token do Bot (do BotFather):", type="password")
    id_tg = st.text_input("Seu Chat ID (do UserInfoBot):")
    
    if st.button("🚀 Testar Conexão e Alerta"):
        res = enviar_alerta_telegram(token_tg, id_tg, f"✅ Terminal InvestSmart Ativo!\nMonitorando: {ticker_input}")
        if res and res.get("ok"):
            st.success("Mensagem enviada com sucesso!")
        else:
            st.error(f"Erro no envio. Verifique Token e ID. Detalhe: {res}")

    st.divider()
    # Auto-Refresh: O gráfico vai recarregar sozinho
    st.write("🔄 Atualização Automática: **Ativa**")
    refresh_rate = st.slider("Intervalo de Atualização (segundos):", 10, 60, 30)

# --- 5. PAINEL PRINCIPAL ---
if ticker_input:
    hist, info = buscar_dados_hb(ticker_input)
    
    if hist is not None and not hist.empty:
        # Indicadores Técnicos
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        resistencia = hist['High'].max()
        suporte = hist['Low'].min()
        vol_atual = hist['Volume'].iloc[-1]
        vol_medio = hist['Volume'].mean()
        
        # Título Dinâmico
        nome_real = info.get('longName', ticker_input)
        st.title(f"📈 {nome_real} | Tempo Real (1 min)")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("🤖 Mentor IA")
            variacao = ((atual / hist['Open'].iloc[0]) - 1) * 100
            st.metric("Preço Atual", f"R$ {atual:,.2f}", f"{variacao:.2f}%")
            
            # RESPOSTA DO MENTOR (CONTEÚDO REAL)
            st.write("---")
            status_vol = "FORTE (Acima da média)" if vol_atual > vol_medio else "FRACO (Abaixo da média)"
            
            # Lógica de Alerta de Rompimento
            if atual >= resistencia * 0.995:
                st.warning("⚠️ Próximo da Resistência!")
                # Envia alerta automático se bater no topo
                if atual >= resistencia:
                    enviar_alerta_telegram(token_tg, id_tg, f"🚨 ROMPIMENTO: {ticker_input} rompeu a máxima do dia em {atual}!")

            st.info(f"Sandro, o volume agora está {status_vol}. "
                    f"O suporte principal de 1 minuto está em R$ {suporte:,.2f}. "
                    "Se houver rompimento do topo com volume, o alerta será enviado ao Telegram.")
            
            # Simulador
            invest = st.number_input("Investimento Simulado (R$):", value=1000.0)
            st.write(f"Você compra: **{invest/atual:.4f}** unidades.")

        with col2:
            # Gráfico Home Broker Profissional
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
            
            # Candles
            fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Minuto'), row=1, col=1)
            # Média Rápida
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='EMA 9', line=dict(color='#ffaa00')), row=1, col=1)
            
            # Volume Colorido
            colors = ['green' if hist.Close[i] >= hist.Open[i] else 'red' for i in range(len(hist))]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
            
            # Linhas de Alerta
            fig.add_hline(y=resistencia, line_dash="dot", line_color="#ff4b4b", annotation_text="RESISTÊNCIA", row=1, col=1)
            fig.add_hline(y=suporte, line_dash="dot", line_color="#00ff00", annotation_text="SUPORTE", row=1, col=1)
            
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=550, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # Mecanismo de Auto-Refresh (Sandro, isso faz o robô girar sozinho)
        time.sleep(refresh_rate)
        st.rerun()

    else:
        st.warning(f"Aguardando dados de {ticker_input}... Verifique se o mercado está aberto ou se o ticker está correto.")
