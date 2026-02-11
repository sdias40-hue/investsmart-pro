import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# 1. Configuracao da Pagina
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# 2. Conexao com a IA
try:
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=CHAVE_API)
except Exception as e:
    st.error("Erro nos Secrets")

# 3. Login
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 InvestSmart Pro | Terminal de Elite")
    chave = st.text_input("Sua Chave de Acesso", type="password")
    if st.button("Entrar"):
        if chave == "sandro2026":
            st.session_state['autenticado'] = True
            st.rerun()
    st.stop()

# --- PAINEL ---
st.title("📈 InvestSmart Pro | Terminal de Elite")
ticker_simples = st.text_input("Ação (ex: VALE3):", "PETR4").upper()
ticker = f"{ticker_simples}.SA" if not ticker_simples.endswith(".SA") else ticker_simples

if st.button("Pedir Análise ao Mentor IA"):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Analise a acao {ticker}")
    st.write(response.text)
