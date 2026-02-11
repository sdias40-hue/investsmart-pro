import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# 1. Configuracao da Pagina
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# 2. Conexao com a IA (Usando segredos do Streamlit)
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

# --- PAINEL PRINCIPAL (APÓS LOGIN) ---
st.title("📈 InvestSmart Pro | Terminal de Elite")

ticker_simples = st.text_input("Código da Ação (ex: VALE3):", "PETR4").upper()
ticker = f"{ticker_simples}.SA" if not ticker_simples.endswith(".SA") else ticker_simples

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("Pedir Análise ao Mentor IA"):
        with st.spinner('O Mentor está analisando...'):
            try:
                # Modelo estavel e alinhamento corrigido
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Faca uma analise profissional da acao {ticker}. Fale sobre o setor.")
                st.success("Análise do Mentor:")
                st.write(response.text)
            except Exception as e:
                st.warning("O Mentor IA está descansando. Tente novamente em breve.")

with col2:
    st.subheader("📊 Monitor de Dividendos")
    try:
        acao_data = yf.Ticker(ticker)
        dividendos = acao_data.dividendos if hasattr(acao_data, 'dividendos') else acao_data.dividends
        if not dividendos.empty:
            st.line_chart(dividendos.tail(15))
            st.dataframe(dividendos.tail(5), use_container_width=True)
        else:
            st.write("Nenhum dividendo encontrado.")
    except:
        st.error("Erro ao carregar dados da Bolsa.")

st.markdown("---")
st.caption("InvestSmart Pro v2.0 | Sandro 2026")
