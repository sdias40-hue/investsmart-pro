import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# 2. Conexão com a Inteligência Artificial (Gemini)
try:
    # O comando deve ser st.secrets para o Streamlit entender
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=CHAVE_API)
except Exception as e:
    st.error("Erro: A chave 'GOOGLE_API_KEY' não foi encontrada nos Secrets.")

# 3. Sistema de Login Protegido
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 InvestSmart Pro | Terminal de Elite")
    st.write("Identifique-se para acessar o painel, Sandro.")
    chave = st.text_input("Sua Chave de Acesso", type="password")
    
    if st.button("Entrar"):
        if chave == "sandro2026":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Chave incorreta! Tente novamente.")
    st.stop()

# --- PAINEL PRINCIPAL (APÓS LOGIN) ---
st.title("📈 InvestSmart Pro | Terminal de Elite")

# Campo para o código da ação
ticker_simples = st.text_input("Código da Ação (ex: VALE3, PETR4):", "PETR4").upper()
ticker = f"{ticker_simples}.SA" if not ticker_simples.endswith(".SA") else ticker_simples

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("Pedir Análise ao Mentor IA"):
        with st.spinner('Analisando mercado...'):
            try:
                # Usando o modelo mais atual (1.5 Flash)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Faça uma análise rápida da ação {ticker}. Fale sobre o setor e dê uma recomendação de cautela ou otimismo."
                response = model.generate_content(prompt)
                st.success("Análise Concluída:")
                st.write(response.text)
            except Exception as e:
                st.warning("O Mentor IA está descansando. Verifique sua chave nos Secrets ou tente em 1 minuto.")

with col2:
    st.subheader("📊 Monitor de Dividendos")
    try:
        acao_data = yf.Ticker(ticker)
        dividendos = acao_data.dividends
        
        if not dividendos.empty:
            st.write(f"Histórico de {ticker}:")
            st.line_chart(dividendos.tail(15))
            st.dataframe(dividendos.tail(5), use_container_width=True)
        else:
            st.write("Nenhum dividendo encontrado para este código.")
    except:
        st.error("Erro ao buscar dados na Yahoo Finance.")

st.markdown("---")
st.caption("InvestSmart Pro v2.0 | Sandro 2026")
