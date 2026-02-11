import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd

# 1. Configuração de Elite
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# Estilo CSS para deixar o visual premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextInput>div>div>input { color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sistema de Login
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 InvestSmart Pro | Terminal de Elite")
    with st.container():
        senha = st.text_input("Chave de Acesso", type="password")
        if st.button("Acessar Terminal"):
            if senha == "sandro2026":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Chave incorreta. Acesso negado.")
    st.stop()

# --- PAINEL PRINCIPAL ---
st.title("📈 InvestSmart Pro | Gestão de Ativos")
st.write(f"Bem-vindo, **Sandro**! O mercado está em constante movimento.")

# Barra lateral para filtros
with st.sidebar:
    st.header("⚙️ Configurações")
    ticker_input = st.text_input("Digite o Ticker (Ex: VALE3, PETR4):", "PETR4").upper()
    periodo = st.selectbox("Período do Gráfico", ["1y", "2y", "5y", "max"])
    st.divider()
    st.caption("Versão 2.0.1 | 2026")

ticker = f"{ticker_input}.SA" if ".SA" not in ticker_input else ticker_input

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🤖 Mentor IA (Análise Fundamentalista)")
    if st.button("✨ Solicitar Análise ao Mentor"):
        with st.spinner("Conectando ao cérebro da IA..."):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                # Rota direta para evitar erro 404 de bibliotecas
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Atue como analista CNPI. Analise a ação {ticker} focando em dividendos e saúde financeira. Seja direto e use bullet points."}]
                    }]
                }
                headers = {'Content-Type': 'application/json'}
                
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                data = response.json()
                
                if response.status_code == 200:
                    analise = data['candidates'][0]['content']['parts'][0]['text']
                    st.success("Análise Concluída com Sucesso!")
                    st.markdown(analise)
                else:
                    st.error(f"Erro na IA: {data['error']['message']}")
            except Exception as e:
                st.error("Falha na conexão direta. Verifique sua chave API.")

with col2:
    st.subheader("📊 Histórico de Proventos")
    try:
        acao = yf.Ticker(ticker)
        # Puxando dados de dividendos
        dividendos = acao.dividends
        
        if not dividendos.empty:
            # Gráfico de linha para os dividendos
            st.line_chart(dividendos.tail(20), use_container_width=True)
            
            st.subheader("📋 Últimos Lançamentos")
            df_divs = dividendos.tail(5).to_frame()
            df_divs.columns = ['Valor (R$)']
            st.dataframe(df_divs.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("Nenhum dado de dividendo encontrado para este ativo.")
            
    except Exception as e:
        st.error(f"Erro ao carregar dados do Yahoo Finance: {e}")

st.divider()
st.info("💡 **Dica do Sistema:** Dividend Yield acima de 6% ao ano é considerado saudável para estratégias de renda passiva.")
