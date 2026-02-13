import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração e Estilo Premium
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="column"] { padding: 0 35px !important; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave", type="password")
    if st.button("Acessar Terminal"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- INTERFACE ---
st.title("🏛️ InvestSmart Pro | Gestão de Ativos")

with st.sidebar:
    st.header("🔍 Radar de Ativos")
    # Campo para digitar
    ticker_input = st.text_input("Digite o Ticker (Ex: MXRF11, JEPP34):", "").upper()
    st.divider()
    # Recuperando as Sugestões Fundamentalistas
    st.subheader("💡 Top 5 Fundamentalistas")
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CMIG4"]
    escolha = st.radio("Sugestões Rápidas:", ["Nenhuma"] + sugestoes)

ticker_final = ticker_input if ticker_input else (escolha if escolha != "Nenhuma" else "")

if ticker_final:
    # Tratamento Inteligente de Ticker (Evita erro de timezone e .SA duplo)
    simbolo = ticker_final.replace(".SA", "")
    simbolo_sa = f"{simbolo}.SA"
    
    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA")
        if st.button("✨ Gerar Análise"):
            with st.spinner("Conectando..."):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    # Forçando Rota v1 para matar o Erro 404
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"Analise a ação {ticker_final} para dividendos."}]}]}
                    res = requests.post(url, json=payload, timeout=10)
                    if res.status_code == 200:
                        st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error("Erro 404 na IA. Verifique sua chave API.")
                except:
                    st.warning("IA em ajuste fino.")

    with col2:
        st.subheader(f"📊 Proventos: {ticker_final}")
        try:
            # Tenta buscar com .SA, se der erro de timezone, tenta puro
            ticker_data = yf.Ticker(simbolo_sa)
            divs = ticker_data.dividends
            if divs.empty:
                ticker_data = yf.Ticker(simbolo)
                divs = ticker_data.dividends
            
            if not divs.empty:
                df = divs.tail(15).to_frame().reset_index()
                df.columns = ['Data', 'Valor']
                # Gráfico de Barras que você aprovou
                chart = alt.Chart(df).mark_bar(size=30, color='#008cff').encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Valor:Q', title='R$'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)
                
                st.subheader("📋 Detalhamento (Precisão: 0.001)")
                df_tab = df.sort_values(by='Data', ascending=False)
                df_tab['Valor'] = df_tab['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_tab, use_container_width=True, hide_index=True)
            else:
                st.info(f"Sem dados de dividendos para {ticker_final}.")
        except:
            st.error("Erro de conexão com a B3.")
else:
    st.info("👋 Use o Radar para selecionar um ativo.")
