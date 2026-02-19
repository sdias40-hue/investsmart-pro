import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Home Broker", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Motor Telegram (Validado pelo Sandro!)
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": mensagem}
            response = requests.post(url, data=data)
            return response.json()
        except: return {"ok": False}
    return {"ok": False}

# 3. Busca de Dados (1 Minuto com Ajuste de Escala)
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

# --- 4. RADAR MASTER ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba_mercado = st.radio("Selecione o Mercado:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "PETR4", "JEPP34"] if aba_mercado == "Ações / BDRs" else ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
    escolha = st.selectbox("Top 5 Recomendadas:", [""] + opcoes)
    ticker_manual = st.text_input("Ou digite o Ticker:", "").upper()
    ticker_final = ticker_manual if ticker_manual else escolha

    st.divider()
    st.header("🔔 Alertas Telegram")
    token_tg = st.text_input("Token Completo:", type="password")
    id_tg = st.text_input("Seu Chat ID (8392660003):")
    
    st.divider()
    refresh_rate = st.slider("Atualizar a cada (seg):", 10, 60, 30)

# --- 5. PAINEL HOME BROKER ---
if ticker_final:
    hist, info = buscar_dados_hb(ticker_final)
    
    if hist is not None and not hist.empty:
        # Cálculos de Análise Estratégica
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        preco_abertura = hist['Open'].iloc[0]
        vol_atual = hist['Volume'].iloc[-1]
        vol_medio = hist['Volume'].mean()
        
        st.title(f"📈 {info.get('longName', ticker_final)} | Tempo Real")
        
        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric("Preço Atual", f"R$ {atual:,.2f}" if "-" not in ticker_final else f"US$ {atual:,.2f}", f"{((atual/preco_abertura)-1)*100:.2f}%")
            
            st.subheader("🤖 Mentor IA | Veredito")
            
            # --- LÓGICA DE ANÁLISE ESTRATÉGICA (O que você pediu) ---
            if atual >= res * 0.998 and vol_atual > vol_medio:
                veredito = "🔥 COMPRA AGORA! Rompimento de topo com volume forte."
                cor_msg = "success"
                enviar_alerta_telegram(token_tg, id_tg, f"🚀 OPORTUNIDADE: {ticker_final} rompeu topo com volume! Preço: {atual}")
            elif atual <= sup * 1.002:
                veredito = "⚠️ QUEDA EM CURSO! O preço está testando o suporte. Não compre agora, aguarde o sinal de reversão."
                cor_msg = "error"
            elif vol_atual < vol_medio * 0.5:
                veredito = "⏳ AGUARDE. O mercado está sem liquidez (volume baixo). Movimento incerto."
                cor_msg = "warning"
            else:
                veredito = "⚖️ NEUTRO. O preço está consolidado. Monitore as extremidades."
                cor_msg = "info"
            
            if cor_msg == "success": st.success(veredito)
            elif cor_msg == "error": st.error(veredito)
            elif cor_msg == "warning": st.warning(veredito)
            else: st.info(veredito)
            
            st.write(f"**Volume:** {'Elevado' if vol_atual > vol_medio else 'Normal'}")
            invest = st.number_input("Simular Investimento:", value=1000.0)
            st.write(f"Você compra: **{invest/atual:.4f}**")

        with c2:
            # Gráfico com Zoom Inteligente e Volume Colorido
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
            
            # Velas (Candlesticks)
            fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='1m'), row=1, col=1)
            
            # Volume Colorido
            cores_vol = ['#26a69a' if hist.Close[i] >= hist.Open[i] else '#ef5350' for i in range(len(hist))]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', marker_color=cores_vol), row=2, col=1)
            
            # Linhas de Suporte e Resistência
            fig.add_hline(y=res, line_dash="dot", line_color="#ef5350", annotation_text="RESISTÊNCIA", row=1, col=1)
            fig.add_hline(y=sup, line_dash="dot", line_color="#26a69a", annotation_text="SUPORTE", row=1, col=1)
            
            # AJUSTE DE VISUALIZAÇÃO (Foco nas Criptos)
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=600, margin=dict(l=0,r=0,t=0,b=0))
            fig.update_yaxes(autorange=True, fixedrange=False, row=1, col=1) # Faz o gráfico focar no preço atual
            
            st.plotly_chart(fig, use_container_width=True)

        time.sleep(refresh_rate)
        st.rerun()
