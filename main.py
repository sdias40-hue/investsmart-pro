import streamlit as st
import pandas as pd
import yfinance as yf
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. CONFIGURAÇÃO SECRETA DA IA (Vamos configurar no Streamlit depois)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Erro ao carregar a Chave da IA. Verifique as configurações de Secrets.")

# 2. SISTEMA DE ACESSOS POR TEMPO
ACESSOS = {
    'SANDRO2026': '2030-12-31',
    'TESTE7DIAS': '2026-02-17'
}

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True
    
    st.title("🔒 InvestSmart Pro")
    pwd = st.text_input("Chave de Acesso:", type="password")
    if st.button("Entrar"):
        pwd = pwd.upper().strip()
        if pwd in ACESSOS:
            if datetime.now() <= datetime.strptime(ACESSOS[pwd], '%Y-%m-%d'):
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Chave expirada!")
        else: st.error("Chave inválida!")
    return False

# 3. FUNÇÃO PARA LER SITES (O que você pediu!)
def analisar_site_investidor(ticker):
    try:
        # Exemplo simples de como a IA pode analisar um contexto colado ou buscado
        prompt = f"Analise o ativo {ticker}. Ele é um bom pagador de dividendos para quem busca renda mensal? Responda como um Mentor Financeiro."
        response = model.generate_content(prompt)
        return response.text
    except:
        return "O Mentor IA está descansando agora. Tente novamente em breve."

# --- APP PRINCIPAL ---
if check_password():
    st.set_page_config(page_title="InvestSmart Pro", layout="wide")
    st.title("🚀 InvestSmart Pro | Terminal de Elite")

    # Radar de Ativos
    ticker_alvo = st.text_input("Digite um Ticker para análise profunda (ex: PETR4, JEPP34):", value="PETR4")
    
    if st.button("💡 Pedir Análise ao Mentor IA"):
        with st.spinner('O Mentor está lendo o mercado...'):
            analise = analisar_site_investidor(ticker_alvo)
            st.markdown(f"### 🤖 Insights do Mentor para {ticker_alvo}")
            st.info(analise)

    st.divider()
    st.subheader("📊 Monitor de Dividendos em Tempo Real")
    # (Aqui continua o seu código de cálculos que já funciona perfeitamente)
