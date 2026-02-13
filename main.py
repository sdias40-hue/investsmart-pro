import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import altair as alt

# 1. Configurações Globais
st.set_page_config(page_title="InvestSmart Pro", layout="wide")

# 2. LOGIN (Simplificado para estabilidade)
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso:", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 3. RADAR E BUSCA
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker = st.text_input("Ticker:", "PETR4").upper()
    st.divider()
    st.caption("Sugestões Rápidas:")
    opcao = st.selectbox("Destaques:", ["", "BBAS3", "TAEE11", "JEPP34", "CMIG4"])
    ticker_final = ticker if ticker != "PETR4" else (opcao if opcao else "PETR4")

# 4. FUNÇÃO DE CONEXÃO BLINDADA (A Diferencial do Projeto)
@st.cache_data(ttl=600) # Mantém os dados por 10 min para evitar bloqueio de IP
def buscar_dados_bolsa(t):
    try:
        # Tenta com .SA (Padrão B3)
        simbolo = f"{t}.SA" if ".SA" not in t else t
        acao = yf.Ticker(simbolo)
        # Força a busca de dividendos ignorando erros de timezone
        divs = acao.dividends
        if divs.empty:
            # Se falhar, tenta sem o .SA (Padrão BDRs/International)
            acao = yf.Ticker(t.replace(".SA", ""))
            divs = acao.dividends
        return divs
    except:
        return pd.Series()

# --- INTERFACE PRINCIPAL ---
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("🤖 Mentor IA")
    if st.button("Analisar"):
        try:
            key = st.secrets["GOOGLE_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
            payload = {"contents": [{"parts": [{"text": f"Dê uma visão técnica sobre os dividendos de {ticker_final}."}]}]}
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
            else:
                st.error(f"Erro IA: {res.status_code}. Verifique a API Key.")
        except:
            st.warning("Servidor de IA ocupado.")

with col2:
    st.subheader(f"📊 Histórico: {ticker_final}")
    proventos = buscar_dados_bolsa(ticker_final)
    
    if not proventos.empty:
        df = proventos.tail(15).to_frame().reset_index()
        df.columns = ['Data', 'Valor']
        # Gráfico Altair (Mais estável que o st.bar_chart para B3)
        chart = alt.Chart(df).mark_bar(size=25, color='#008cff').encode(
            x='Data:T', y='Valor:Q', tooltip=['Data', 'Valor']
        ).properties(height=350)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(df.sort_values(by='Data', ascending=False), hide_index=True)
    else:
        st.error(f"Erro de comunicação: A bolsa não respondeu para {ticker_final}. Tente CMIG4.")

st.caption("InvestSmart Pro v25.0 | Foco em Conectividade B3")
