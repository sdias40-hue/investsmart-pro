import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Motor de Alerta Universal (Para o seu cliente configurar)
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": mensagem}
            response = requests.post(url, data=data)
            return response.json()
        except: return {"ok": False}
    return {"ok": False}

# 3. Busca de Dados com Filtro de Erros
def buscar_dados_hb(t):
    try:
        ticker_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(ticker_search)
        hist = ticker.history(period="1d", interval="1m")
        if hist.empty:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="1d", interval="1m")
        return hist, ticker.info
    except: return None, None

# --- 4. PAINEL DE CONFIGURAÇÃO DO CLIENTE ---
with st.sidebar:
    st.header("🔑 Licença e Configuração")
    st.info("Insira os dados do seu Bot para receber os sinais de compra/venda.")
    token_cliente = st.text_input("Token do seu ChatBot:", type="password", help="Pegue no @BotFather")
    id_cliente = st.text_input("Seu Chat ID:", help="Pegue no @userinfobot")
    
    if st.button("🚀 Ativar e Testar Robô"):
        res = enviar_alerta_telegram(token_cliente, id_cliente, "✅ Sistema InvestSmart Pro Ativado! Monitorando mercado...")
        if res.get("ok"): st.success("Conexão com seu Bot OK!")
        else: st.error("Falha na conexão. Verifique Token/ID.")

    st.divider()
    st.header("🔍 Radar de Ativos")
    aba_mercado = st.radio("Mercado:", ["Ações", "ETFs / BDRs", "Criptos"])
    opcoes = ["PETR4", "VALE3", "BBAS3"] if aba_mercado == "Ações" else ["JEPP34", "BOVA11", "IVVB11"]
    if aba_mercado == "Criptos": opcoes = ["BTC-USD", "ETH-USD", "SOL-USD"]
    
    ticker_final = st.text_input("Ticker Manual:", "").upper() or st.selectbox("Principais:", [""] + opcoes)

# --- 5. ANALISADOR ESTRATÉGICO ---
if ticker_final:
    hist, info = buscar_dados_hb(ticker_final)
    
    if hist is not None and not hist.empty:
        # Correção do erro: Cálculo seguro da média
        hist['EMA9'] = hist['Close'].ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        
        st.title(f"🏛️ Terminal {ticker_final} | {info.get('sector', 'Ativo Global')}")
        
        c1, c2 = st.columns([1, 2.8])
        with c1:
            st.metric("Preço", f"R$ {atual:,.2f}" if "-" not in ticker_final else f"US$ {atual:,.2f}")
            st.subheader("🤖 Mentor IA")
            
            # Lógica de Veredito Setorial
            ramo = info.get('industry', 'Investimentos')
            if atual >= res * 0.999:
                st.success(f"🔥 COMPRA! Rompimento no setor de {ramo}.")
                enviar_alerta_telegram(token_cliente, id_cliente, f"🚨 SINAL DE COMPRA: {ticker_final} rompendo resistência em {atual}!")
            elif atual <= sup * 1.001:
                st.error("📉 QUEDA! Risco alto, evite compra agora.")
            else:
                st.info(f"O ativo de {ramo} está em zona neutra. Aguarde sinal de volume.")

        with c2:
            # Gráfico de Alta Definição (Criptos Nítidas)
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='1m'), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='Média', line=dict(color='#ffaa00', width=1)), row=1, col=1)
            
            # Volume Colorido
            cv = ['#26a69a' if hist.Close[i] >= hist.Open[i] else '#ef5350' for i in range(len(hist))]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=cv, name='Vol'), row=2, col=1)
            
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=550, margin=dict(l=0,r=0,t=0,b=0))
            fig.update_yaxes(autorange=True, fixedrange=False, row=1, col=1)
            st.plotly_chart(fig, use_container_width=True)

        time.sleep(30)
        st.rerun()
