import streamlit as st
import yfinance as yf
import requests
import json

# 1. Configuracao da Pagina
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Login InvestSmart Pro")
    senha = st.text_input("Chave", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- PAINEL PRINCIPAL ---
st.title("📈 InvestSmart Pro | Terminal de Elite")
ticker_input = st.text_input("Ação (ex: VALE3):", "PETR4").upper()
ticker = f"{ticker_input}.SA" if ".SA" not in ticker_input else ticker_input

col1, col2 = st.columns(2)

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("Analisar com IA"):
        with st.spinner("Analisando mercado via Rota Direta..."):
            try:
                # O NOVO CAMINHO: Chamada direta para a API v1 estável
                api_key = st.secrets["GOOGLE_API_KEY"]
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {"contents": [{"parts": [{"text": f"Analise a acao {ticker}. Seja breve."}]}]}
                headers = {'Content-Type': 'application/json'}
                
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                data = response.json()
                
                if response.status_code == 200:
                    texto = data['candidates'][0]['content']['parts'][0]['text']
                    st.write(texto)
                else:
                    st.error(f"Erro na API: {data['error']['message']}")
            except Exception as e:
                st.error(f"Erro de Conexão: {str(e)}")

with col2:
    st.subheader("📊 Dividendos")
    try:
        dados = yf.Ticker(ticker)
        # Mantendo seu grafico profissional que ja funciona
        st.line_chart(dados.dividends.tail(15))
    except:
        st.write("Dados da bolsa indisponíveis.")
