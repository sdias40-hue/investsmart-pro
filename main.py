import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd

# 1. Configuração de Página e Visual Premium
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.title("🔐 Terminal InvestSmart Pro")
    senha = st.text_input("Chave de Acesso", type="password")
    if st.button("Acessar Sistema"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Ativos")
st.write(f"Bem-vindo, **Sandro**! Sua visão estratégica do mercado.")

# Sidebar organizada
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_input = st.text_input("Ticker (Ex: VALE3, PETR4, JEPP34):", "PETR4").upper()
    ticker = f"{ticker_input}.SA" if ".SA" not in ticker_input else ticker_input
    periodo_grafico = st.selectbox("Histórico", ["1y", "2y", "5y", "max"])
    st.divider()
    st.caption("InvestSmart Pro v15.0 | 2026")

col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("🤖 Mentor IA (Análise CNPI)")
    if st.button("✨ Gerar Análise de Dividendos"):
        with st.spinner("Consultando inteligência de mercado..."):
            try:
                key = st.secrets["GOOGLE_API_KEY"]
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": f"Analise o histórico de dividendos de {ticker}. Vale a pena para renda passiva? Seja direto."}]}]}
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    st.info(response.json()['candidates'][0]['content']['parts'][0]['text'])
                else:
                    st.warning("IA em manutenção. Use os dados técnicos ao lado.")
            except:
                st.error("Erro na conexão com o Mentor.")

with col2:
    st.subheader("📊 Histórico de Proventos (Barras)")
    try:
        acao = yf.Ticker(ticker)
        divs = acao.dividends
        
        if not divs.empty:
            # Criando o DataFrame para o gráfico de barras
            df_divs = divs.tail(15).to_frame()
            df_divs.columns = ['Valor (R$)']
            
            # EXIBINDO GRÁFICO DE BARRAS (Muito mais profissional)
            st.bar_chart(df_divs, color="#008cff")
            
            # Tabela detalhada logo abaixo
            st.subheader("📋 Detalhamento de Pagamentos")
            st.dataframe(df_divs.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("Nenhum registro de dividendo encontrado para este ativo.")
    except Exception as e:
        st.error(f"Erro ao conectar com dados da B3: {e}")

st.divider()
st.caption("⚠️ Dados obtidos via Yahoo Finance API. A análise da IA é educativa e não constitui recomendação de compra.")
