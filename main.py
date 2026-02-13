import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

# 1. Setup de Elite
st.set_page_config(page_title="InvestSmart Pro | Mentor", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA E NOTÍCIAS ---
def buscar_noticias(ticker):
    try:
        url = f"https://www.google.com/search?q=noticias+hoje+sobre+{ticker}&tbm=nws"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        noticias = [n.get_text() for n in soup.find_all('div', limit=3)]
        return " | ".join(noticias[:2])
    except: return "Sem notícias relevantes no momento."

def buscar_dados(t):
    for s in [f"{t}.SA", t, t.replace(".SA", "")]:
        obj = yf.Ticker(s); h = obj.history(period="60d")
        if not h.empty: return obj, h, obj.info
    return None, None, None

# --- 4. INTERFACE ---
st.title("🏛️ InvestSmart Pro | Terminal Mentor")

with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["VULC3", "BBAS3", "TAEE11", "JEPP34"] if aba == "Ações / BDRs" else ["BTC-USD", "SOL-USD", "ETH-USD"]
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or st.selectbox("Favoritos:", [""] + opcoes)

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    if hist is not None:
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]; ma9 = hist['EMA9'].iloc[-1]
        
        col1, col2 = st.columns([1, 2.3])
        with col1:
            st.subheader("🤖 Veredito do Mentor")
            st.metric(f"Preço {ticker_final}", f"R$ {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            
            # CONSELHO HÍBRIDO (Visto no image_f547a5.png)
            if atual > ma9: st.success("✅ GATILHO ATIVADO: Tendência de alta confirmada!")
            else: st.error("📉 AGUARDE: Gráfico ainda em queda.")
            
            st.info(f"📍 Setor: {info.get('sector', 'Global')}")
            st.write(f"**Veredito:** {'💎 BOA PARA COMPRAR' if atual > ma9 else '⏳ NÃO COMPENSA AGORA'}")

        with col2:
            st.subheader("📊 Gráfico Candlestick (Profissional)")
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close)])
            fig.add_trace(go.Scatter(x=hist.index, y=hist.EMA9, name='Gatilho', line=dict(color='#ffaa00')))
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        # 5. CHATBOT COM NOTÍCIAS REAIS (O que você pediu)
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Pergunte sobre o mercado ou este ativo:")
        if pergunta:
            news = buscar_noticias(ticker_final)
            st.write(f"**Mentor responde:** Analisando '{pergunta}'... Hoje o mercado está influenciado por: {news}. Graficamente, o ativo está em {'alta' if atual > ma9 else 'queda'}.")

else: st.info("👋 Selecione um ativo para iniciar.")
