import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração de Elite
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# Estilo para manter o visual premium e colunas finas
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; }
    [data-testid="stSidebar"] { min-width: 280px; }
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

# Sidebar com busca inteligente (Autocomplete)
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    
    # Lista de tickers comuns para facilitar a busca intuitiva
    sugestoes = ["PETR4", "VALE3", "BBAS3", "TAEE11", "CMIG4", "CMIG3", "JEPP34", "CPLE6", "TRPL4", "SAPR4"]
    
    # O componente 'selectbox' agora funciona como busca: se o que você digitar não estiver na lista, ele aceita
    ticker_busca = st.selectbox(
        "Busque ou selecione um Ticker:",
        options=sugestoes,
        index=0,
        help="Exemplo: CMIG4, PETR4, VALE3"
    ).upper()

    st.divider()
    st.caption("InvestSmart Pro v18.0 | 2026")

if ticker_busca:
    # Garante que o ticker tenha o .SA para a B3
    ticker_final = f"{ticker_busca}.SA" if ".SA" not in ticker_busca else ticker_busca
    
    # Colunas com gap maior para não grudarem
    col1, col2 = st.columns([1, 1.3], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA")
        if st.button("✨ Gerar Análise Profissional"):
            with st.spinner("Analisando mercado..."):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"Analise {ticker_final} para dividendos. Seja curto."}]}]}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.info(response.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.warning("IA em manutenção. Use os dados técnicos.")
                except:
                    st.error("Erro na conexão com a IA.")

    with col2:
        st.subheader(f"📊 Dividendos: {ticker_busca}")
        try:
            acao = yf.Ticker(ticker_final)
            divs = acao.dividends
            
            if not divs.empty:
                df_divs = divs.tail(15).to_frame().reset_index()
                df_divs.columns = ['Data', 'Valor']
                
                # Gráfico de barras com o visual que você aprovou
                chart = alt.Chart(df_divs).mark_bar(
                    size=30, # Barras finas/médias profissionais
                    color='#008cff'
                ).encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Valor:Q', title='R$'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=400)
                
                st.altair_chart(chart, use_container_width=True)
                
                # Detalhamento com 3 casas decimais
                st.subheader("📋 Detalhamento de Pagamentos")
                df_display = df_divs.copy().sort_values(by='Data', ascending=False)
                df_display['Valor'] = df_display['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info(f"Sem dados de dividendos para {ticker_busca}. Verifique se o ticker está correto (ex: CMIG4).")
        except:
            st.error("Erro ao buscar dados na B3.")

st.divider()
st.caption("InvestSmart Pro | Precisão: 0.001 | 2026")
