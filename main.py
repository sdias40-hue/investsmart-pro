import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. CSS de Elite para separação de colunas
st.set_page_config(page_title="InvestSmart Pro", layout="wide")
st.markdown("""
    <style>
    [data-testid="column"] { padding: 0 40px !important; } /* Separa as colunas */
    .main { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# 2. Login Simples
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# 3. Radar de Ativos
with st.sidebar:
    st.header("🔍 Radar")
    ticker = st.text_input("Ticker (Ex: MXRF11, JEPP34):", "PETR4").upper()

if ticker:
    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA")
        if st.button("Analisar"):
            try:
                key = st.secrets["GOOGLE_API_KEY"]
                # URL BLINDADA (v1 oficial)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": f"Analise {ticker} para dividendos."}]}]}
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                else:
                    st.error("Erro 404: Verifique se sua API Key é nova.")
            except:
                st.warning("IA Indisponível.")

    with col2:
        st.subheader(f"📊 Proventos: {ticker}")
        try:
            # TENTA COM .SA, SE FALHAR TENTA SEM (Para BDRs e FIIs)
            data = yf.Ticker(f"{ticker}.SA")
            divs = data.dividends
            if divs.empty:
                data = yf.Ticker(ticker)
                divs = data.dividends
            
            if not divs.empty:
                df = divs.tail(15).to_frame().reset_index()
                df.columns = ['Data', 'Valor']
                chart = alt.Chart(df).mark_bar(size=30, color='#008cff').encode(
                    x='Data:T', y='Valor:Q'
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df.sort_values(by='Data', ascending=False), hide_index=True)
            else:
                st.info("Nenhum dado encontrado.")
        except:
            st.error("Erro na busca.")

st.caption("InvestSmart Pro v22.0 | Limpeza de Pendências")
