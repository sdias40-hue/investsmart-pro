import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# 1. Configuracao da Pagina
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# 2. Conexao com a IA (Usando a nova biblioteca e secrets)
try:
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=CHAVE_API)
except Exception as e:
    st.error("Erro nos Secrets: Verifique se a chave GOOGLE_API_KEY foi adicionada.")

# 3. Sistema de Login
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 InvestSmart Pro | Terminal de Elite")
    chave = st.text_input("Sua Chave de Acesso", type="password")
    if st.button("Entrar"):
        if chave == "sandro2026":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Chave incorreta!")
    st.stop()

# --- PAINEL PRINCIPAL ---
st.title("📈 InvestSmart Pro | Terminal de Elite")

ticker_input = st.text_input("Código da Ação (ex: VALE3):", "PETR4").upper()
ticker = f"{ticker_input}.SA" if not ticker_input.endswith(".SA") else ticker_input

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("Pedir Análise ao Mentor IA"):
        with st.spinner('O Mentor está analisando o mercado...'):
            try:
                # Modelo estavel e alinhamento perfeito
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Faca uma analise resumida da acao {ticker}. Dê uma dica para o investidor."
                response = model.generate_content(prompt)
                st.success("Análise do Mentor:")
                st.write(response.text)
            except Exception as e:
                st.warning("O Mentor IA está descansando. Verifique se sua cota gratuita no Google AI Studio expirou.")

with col2:
    st.subheader("📊 Monitor de Dividendos")
    try:
        dados = yf.Ticker(ticker)
        divs = dados.dividends
        if not divs.empty:
            st.line_chart(divs.tail(15))
            st.write("Últimos pagamentos:")
            st.dataframe(divs.tail(5), use_container_width=True)
        else:
            st.info("Nenhum dividendo encontrado para este código.")
    except Exception as e:
        st.error("Erro ao carregar dados da Bolsa.")

st.markdown("---")
st.caption("InvestSmart Pro v2.0 | Sandro 2026")
