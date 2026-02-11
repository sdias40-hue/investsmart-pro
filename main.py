import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração de Página com Tema Escuro Profissional
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; height: 3em; }
    /* Ajuste fino na largura da sidebar */
    [data-testid="stSidebar"] { min-width: 280px; max-width: 320px; }
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

# Sidebar com busca intuitiva e automática
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    
    # Lista automática das 5 do dia + Opção para digitar
    lista_radar = ["Escolha uma ação...", "JEPP34", "BBAS3", "TAEE11", "PETR4", "CPLE6", "Digitar Ticker..."]
    escolha = st.selectbox("Ações em Destaque:", lista_radar)
    
    ticker_final = ""
    
    if escolha == "Digitar Ticker...":
        # Se escolher digitar, abre o campo de texto
        ticker_input = st.text_input("Digite o Ticker (Ex: VALE3):", "").upper()
        ticker_final = ticker_input
    elif escolha != "Escolha uma ação...":
        # Se escolher uma da lista, ela vira o ticker final
        ticker_final = escolha

    st.divider()
    st.caption("Radar Inteligente v17.0 | 2026")

if ticker_final:
    ticker_simbolo = f"{ticker_final}.SA" if ".SA" not in ticker_final else ticker_final
    
    # O PULO DO GATO: Usando gap="large" para separar bem as colunas
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA")
        if st.button("✨ Gerar Análise CNPI"):
            with st.spinner("Analisando mercado..."):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"Analise {ticker_simbolo} para dividendos."}]}]}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.info(response.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.warning("Servidor ocupado. Tente em instantes.")
                except:
                    st.error("Erro na conexão com a IA.")

    with col2:
        st.subheader(f"📊 Dividendos: {ticker_final}")
        try:
            acao = yf.Ticker(ticker_simbolo)
            divs = acao.dividends
            
            if not divs.empty:
                df_divs = divs.tail(15).to_frame().reset_index()
                df_divs.columns = ['Data', 'Valor']
                
                # Gráfico com barras largas e espaçadas
                chart = alt.Chart(df_divs).mark_bar(
                    size=30, # Barras robustas
                    color='#008cff',
                    cornerRadiusTopLeft=3,
                    cornerRadiusTopRight=3
                ).encode(
                    x=alt.X('Data:T', title='Data de Pagamento'),
                    y=alt.Y('Valor:Q', title='Rendimento (R$)'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=400).configure_view(strokeOpacity=0)
                
                st.altair_chart(chart, use_container_width=True)
                
                # Detalhamento Profissional
                st.subheader("📋 Detalhamento dos Proventos")
                df_display = df_divs.copy().sort_values(by='Data', ascending=False)
                df_display['Valor'] = df_display['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("Aguardando dados oficiais de dividendos para este ticker.")
        except Exception as e:
            st.error("Ativo não encontrado ou erro de conexão com a B3.")
else:
    st.info("👋 Selecione uma ação no Radar ou digite o código para começar.")

st.divider()
st.caption("InvestSmart Pro | Precisão de 3 casas decimais | Dados: Yahoo Finance 2026")
