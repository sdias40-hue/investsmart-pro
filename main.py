import streamlit as st
import yfinance as yf
import requests
import json

# 1. Configuração Visual
st.set_page_config(page_title="InvestSmart Pro", layout="wide")

# 2. Login Direto
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Acesso InvestSmart Pro")
    senha = st.text_input("Chave", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- TERMINAL ---
st.title("📈 Terminal InvestSmart Pro")

with st.sidebar:
    ticker_input = st.text_input("Ticker:", "PETR4").upper()
    ticker = f"{ticker_input}.SA" if ".SA" not in ticker_input else ticker_input
    st.caption("Versão Final 2026")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("🚀 Gerar Análise"):
        with st.spinner("Conectando..."):
            try:
                # O CAMINHO MAIS CURTO: Usando a URL que o Google não bloqueia
                key = st.secrets["GOOGLE_API_KEY"]
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                
                payload = {"contents": [{"parts": [{"text": f"Analise rápida da ação {ticker} para dividendos."}]}]}
                response = requests.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    st.write(data['candidates'][0]['content']['parts'][0]['text'])
                else:
                    # Se o Flash falhar, tentamos o Pro automaticamente
                    url_pro = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={key}"
                    response_pro = requests.post(url_pro, json=payload)
                    st.write(response_pro.json()['candidates'][0]['content']['parts'][0]['text'])
            except:
                st.warning("IA temporariamente indisponível. O gráfico abaixo continua operacional.")

with col2:
    st.subheader("📊 Histórico de Dividendos")
    try:
        acao = yf.Ticker(ticker)
        divs = acao.dividends
        if not divs.empty:
            st.line_chart(divs.tail(20))
            st.dataframe(divs.tail(5))
        else:
            st.info("Sem dividendos cadastrados.")
    except:
        st.error("Erro ao conectar com a B3.")
