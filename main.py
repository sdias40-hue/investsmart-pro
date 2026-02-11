import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# Puxar a chave dos Secrets do Streamlit
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("Erro: Chave API não configurada nos Secrets do Streamlit.")

# Interface de Login
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 InvestSmart Pro | Terminal de Elite")
    chave = st.text_input("Chave de Acesso", type="password")
    if st.button("Entrar"):
        if chave == "sandro2026":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Chave inválida!")
    st.stop()

# --- ÁREA DO TERMINAL APÓS LOGIN ---
st.title("📈 InvestSmart Pro | Terminal de Elite")

ticker = st.text_input("Digite o código da ação (ex: PETR4.SA):", "PETR4.SA").upper()
if not ticker.endswith(".SA") and len(ticker) <= 5:
    ticker += ".SA"

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("Pedir Análise ao Mentor IA"):
        try:
            # USANDO O MODELO MAIS ATUAL E RÁPIDO
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Faça uma análise rápida e profissional da ação {ticker} para um investidor. Fale sobre o setor e o que esperar."
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            st.warning("O Mentor IA está descansando agora. Tente novamente em 1 minuto.")
            st.info("Dica: Verifique se sua chave API está correta nos Secrets.")

with col2:
    st.subheader("📊 Monitor de Dividendos")
    try:
        acao = yf.Ticker(ticker)
        divs = acao.dividends
        if not divs.empty:
            st.line_chart(divs.tail(10))
            st.write("Últimos dividendos pagos:")
            st.dataframe(divs.tail(5))
        else:
            st.write("Nenhum dividendo recente encontrado.")
    except:
        st.error("Erro ao carregar dados da Bolsa.")

st.markdown("---")
st.caption("InvestSmart Pro - Desenvolvido por Sandro | 2026")
