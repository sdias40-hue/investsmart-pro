import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração de Página e Identidade Visual
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    /* Força o espaçamento entre colunas */
    [data-testid="column"] { padding: 0 25px; }
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

# Sidebar com busca de "Campo Aberto"
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    
    # Lista de sugestões rápidas
    sugestoes = ["Selecione ou Digite...", "PETR4", "VALE3", "BBAS3", "TAEE11", "CMIG4", "JEPP34", "GRND3"]
    
    # Selectbox que permite ao usuário ver as top 5 ou digitar livremente
    escolha = st.selectbox("Ativos no Radar:", sugestoes)
    
    ticker_final = ""
    if escolha == "Selecione ou Digite...":
        ticker_final = st.text_input("Digite o Ticker (Ex: CMIG4, SAPR4):").upper()
    else:
        ticker_final = escolha

    st.divider()
    st.caption("InvestSmart Pro v19.0 | 2026")

if ticker_final:
    # Ajuste automático do sufixo B3
    ticker_simbolo = f"{ticker_final}.SA" if ".SA" not in ticker_final else ticker_final
    
    # Layout com espaçamento real (gap="large" reforçado pelo CSS)
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA (Visão CNPI)")
        if st.button("✨ Solicitar Análise Estratégica"):
            with st.spinner("O Mentor está processando os dados..."):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    # Rota direta para máxima estabilidade
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"Analise a ação {ticker_final} focando em dividendos e setor. Seja técnico."}]}]}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.info(response.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.warning("IA em ajuste fino. Verifique os dados técnicos ao lado.")
                except:
                    st.error("Conexão com Mentor IA indisponível no momento.")

    with col2:
        st.subheader(f"📊 Histórico de Proventos: {ticker_final}")
        try:
            dados_ativo = yf.Ticker(ticker_simbolo)
            divs = dados_ativo.dividends
            
            if not divs.empty:
                df_divs = divs.tail(15).to_frame().reset_index()
                df_divs.columns = ['Data', 'Valor']
                
                # Gráfico com barras separadas e design premium
                chart = alt.Chart(df_divs).mark_bar(
                    size=28, # Tamanho ideal para não grudar
                    color='#008cff',
                    cornerRadiusTopLeft=4,
                    cornerRadiusTopRight=4
                ).encode(
                    x=alt.X('Data:T', title='Data do Pagamento'),
                    y=alt.Y('Valor:Q', title='Valor (R$)'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=400)
                
                st.altair_chart(chart, use_container_width=True)
                
                # Tabela de Detalhamento com 3 casas
                st.subheader("📋 Detalhamento (Precisão: 0.001)")
                df_tab = df_divs.copy().sort_values(by='Data', ascending=False)
                df_tab['Valor'] = df_tab['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_tab, use_container_width=True, hide_index=True)
            else:
                st.warning(f"Não encontramos histórico de dividendos para {ticker_final}. Tente CMIG4 ou PETR4.")
        except:
            st.error("Erro ao acessar dados da B3 para este ativo.")
else:
    st.info("👋 Para começar, selecione um ativo na lista ao lado ou digite o código da ação.")

st.divider()
st.caption("InvestSmart Pro | Terminal de Elite 2026")
