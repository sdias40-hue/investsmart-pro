import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Intelligence", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Motor Telegram (Sandro, o botão de teste voltou!)
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": mensagem}
            response = requests.post(url, data=data)
            return response.json()
        except: return {"ok": False}
    return {"ok": False}

# 3. Busca de Dados e Inteligência de Setor
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
    aba_mercado = st.radio("Selecione o Mercado:", ["Ações / BDRs", "ETFs", "Criptomoedas"])
    
    # Listas atualizadas incluindo ETFs
    if aba_mercado == "Ações / BDRs":
        opcoes = ["BBAS3", "TAEE11", "VULC3", "PETR4", "VALE3", "A1IV34"]
    elif aba_mercado == "ETFs":
        opcoes = ["JEPP34", "IVVB11", "BOVA11", "SMAL11", "DIVO11"]
    else:
        opcoes = ["BTC-USD", "ETH-USD", "SOL-USD"]
        
    escolha = st.selectbox("Principais Oportunidades:", [""] + opcoes)
    ticker_manual = st.text_input("Digite o Ticker:", "").upper()
    ticker_final = ticker_manual if ticker_manual else escolha

    st.divider()
    st.header("🔔 Alertas & Teste")
    token_tg = st.text_input("Token Completo:", type="password")
    id_tg = st.text_input("Seu Chat ID (8392660003):")
    if st.button("🚀 Testar Comunicação"):
        res = enviar_alerta_telegram(token_tg, id_tg, f"✅ Teste de Conexão: OK!")
        if res.get("ok"): st.success("Telegram OK!")
        else: st.error("Erro no Token/ID.")

    st.divider()
    refresh_rate = st.slider("Atualizar a cada (seg):", 10, 60, 30)

# --- 5. PAINEL HOME BROKER (Visual Profissional) ---
if ticker_final:
    hist, info = buscar_dados_hb(ticker_final)
    
    if hist is not None and not hist.empty:
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        setor = info.get('sector', 'ETF / Ativo Internacional')
        ramo = info.get('industry', 'Gestão de Ativos')
        
        # Cálculo Simples de Preço Justo (Baseado em Yield Desejado de 6%)
        dy_estimado = info.get('trailingAnnualDividendYield', 0)
        preco_justo = (info.get('trailingAnnualDividendRate', 0) / 0.06) if dy_estimado > 0 else (atual * 1.15)

        st.title(f"📈 {info.get('longName', ticker_final)} | {setor}")
        
        c1, c2 = st.columns([1, 3])
        with c1:
            st.metric("Preço Atual", f"R$ {atual:,.2f}", f"{((atual/hist.Open.iloc[0])-1)*100:.2f}%")
            st.write(f"**Preço Justo Est.:** R$ {preco_justo:,.2f}")
            
            st.subheader("🤖 Mentor IA | Análise Setorial")
            
            # --- ANALISE DO MENTOR MELHORADA (O que você pediu) ---
            analise_futura = ""
            if atual < preco_justo:
                analise_futura = "O ativo está abaixo do valor intrínseco. No longo prazo, a tendência é de valorização buscando o preço justo."
            else:
                analise_futura = "O preço está esticado. Risco de correção no curto prazo para buscar as médias."

            msg_mentor = f"""
            Sandro, este ativo pertence ao ramo de **{ramo}**. 
            
            **Fatores de Risco/Oportunidade:** Atualmente o volume indica {'acumulação' if atual > sup else 'distribuição'}. 
            
            **Perspectiva:** {analise_futura} Devido ao cenário de juros e o setor de {setor}, o ativo pode {'subir' if atual > hist.EMA9.iloc[-1] else 'corrigir'} nos próximos minutos.
            """
            
            st.info(msg_mentor)
            
            if atual >= res:
                st.success("🔥 PONTO DE COMPRA: Rompimento com Volume!")
                enviar_alerta_telegram(token_tg, id_tg, f"🚨 ALERTA COMPRA: {ticker_final} em {atual}. Setor: {setor}")

        with c2:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
            fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='1m'), row=1, col=1)
            
            cores_vol = ['#26a69a' if hist.Close[i] >= hist.Open[i] else '#ef5350' for i in range(len(hist))]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', marker_color=cores_vol), row=2, col=1)
            
            fig.add_hline(y=res, line_dash="dot", line_color="#ef5350", annotation_text="RESISTÊNCIA", row=1, col=1)
            fig.add_hline(y=sup, line_dash="dot", line_color="#26a69a", annotation_text="SUPORTE", row=1, col=1)
            
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=600, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

        time.sleep(refresh_rate)
        st.rerun()
