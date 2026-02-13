import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração de Elite e CSS
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="column"] { padding: 0 25px; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sistema de Login
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

with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_manual = st.text_input("Digite o Ticker (Ex: VULC3, JEPP34):", "").upper()
    
    st.divider()
    st.subheader("💡 Top 5 Fundamentalistas")
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CPLE6"]
    escolha_sugestao = st.radio("Radar Rápido:", ["Nenhuma"] + sugestoes)
    st.caption("Terminal v21.0 | 2026")

ticker_final = ticker_manual if ticker_manual else (escolha_sugestao if escolha_sugestao != "Nenhuma" else "")

if ticker_final:
    # Tratamento de Ticker para B3 e BDRs
    ticker_simbolo = f"{ticker_final}.SA" if len(ticker_final) <= 5 and ".SA" not in ticker_final else ticker_final
    
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA (Visão CNPI)")
        if st.button("✨ Solicitar Análise"):
            with st.spinner("Conectando ao Mentor..."):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    # ROTA DIRETA: Evita o erro 404 das bibliotecas
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"Analise a ação {ticker_final} para dividendos. Seja técnico."}]}]}
                    response = requests.post(url, json=payload)
                    
                    if response.status_code == 200:
                        st.info(response.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.warning("Servidor ocupado. Use os dados técnicos ao lado.")
                except:
                    st.error("Erro na conexão com a IA.")

    with col2:
        st.subheader(f"📊 Histórico de Proventos: {ticker_final}")
        try:
            acao = yf.Ticker(ticker_simbolo)
            divs = acao.dividends
            if not divs.empty:
                df_divs = divs.tail(15).to_frame().reset_index()
                df_divs.columns = ['Data', 'Valor']
                
                # Gráfico de Barras Profissional (Como no print da VULC3)
                chart = alt.Chart(df_divs).mark_bar(size=30, color='#008cff').encode(
                    x=alt.X('Data:T', title='Data do Pagamento'),
                    y=alt.Y('Valor:Q', title='Valor (R$)'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)
                
                # Detalhamento de Precisão
                st.subheader("📋 Detalhamento (Precisão: 0.001)")
                df_tab = df_divs.sort_values(by='Data', ascending=False)
                df_tab['Valor'] = df_tab['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_tab, use_container_width=True, hide_index=True)
            else:
                st.warning(f"Sem histórico de dividendos para {ticker_final}.")
        except:
            st.error("Erro ao acessar dados da B3.")
else:
    st.info("👋 Digite um ticker no Radar para iniciar.")
