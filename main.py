import streamlit as st
import yfinance as yf
import google.generativeai as genai
import os

# 1. Configuracao da Pagina
st.set_page_config(page_title="InvestSmart Pro", layout="wide")

# 2. Comando para forcar a versao oficial da API
os.environ["GOOGLE_GENAI_USE_V1"] = "true"

# 3. Conexao com a IA
try:
    CHAVE = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=CHAVE)
except:
    st.error("Erro na Chave API nos Secrets")

# 4. Login
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
        with st.spinner("Analisando..."):
            try:
                # Chamada limpa do modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Analise a acao {ticker}")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro na IA: {str(e)}")

with col2:
    st.subheader("📊 Dividendos")
    try:
        dados = yf.Ticker(ticker)
        st.line_chart(dados.dividends.tail(15))
    except:
        st.write("Dados da bolsa indisponíveis agora.")
