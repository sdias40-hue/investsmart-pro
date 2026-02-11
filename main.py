import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# 2. Conexão com o Cérebro (IA) - Pegando a chave dos Secrets
try:
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=CHAVE_API)
except Exception as e:
    st.error("Erro: A chave 'GOOGLE_API_KEY' não foi encontrada nos Secrets do Streamlit.")

# 3. Sistema de Login
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 InvestSmart Pro | Terminal de Elite")
    st.write("Bem-vindo, Sandro! Por favor, identifique-se.")
    chave = st.text_input("Digite sua Chave de Acesso", type="password")
    
    if st.button("Entrar"):
        if chave == "sandro2026":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Chave de acesso incorreta!")
    st.stop()

# --- ÁREA LOGADA DO TERMINAL ---
st.title("📈 InvestSmart Pro | Terminal de Elite")

# Input do Ticker com ajuda automática
ticker_input = st.text_input("Digite o código da ação (ex: VALE3):", "PETR4").upper()
ticker = f"{ticker_input}.SA" if not ticker_input.endswith(".SA") else ticker_input

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("Pedir Análise ao Mentor IA"):
        with st.spinner('Consultando inteligência de mercado...'):
            try:
                # Usando o modelo mais moderno e gratuito
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Faça uma análise rápida da ação {ticker}. Diga se o setor está em alta e dê uma dica de ouro para o investidor."
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.warning("O Mentor IA está descansando agora. Tente novamente em 1 minuto.")
                st.write("Dica: Verifique se sua chave API no Google AI Studio ainda está ativa.")

with col2:
    st.subheader("📊 Monitor de Dividendos")
    try:
        dados_acao = yf.Ticker(ticker)
        proventos = dados_acao.dividends
        
        if not proventos.empty:
            st.write(f"Histórico de pagamentos de {ticker}:")
            st.line_chart(proventos.tail(15))
            st.dataframe(proventos.tail(5), use_container_width=True)
        else:
            st.write("Nenhum dividendo recente encontrado para este ativo.")
    except:
        st.error("Não foi possível conectar com a Bolsa de Valores agora.")

st.markdown("---")
st.caption(f"InvestSmart Pro v2.0 | Desenvolvido por Sandro | 2026")
