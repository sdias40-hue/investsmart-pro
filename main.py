import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração de Página e Estilo (Foco em Separação)
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")
st.markdown("<style>[data-testid='column'] { padding: 0 40px !important; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    with st.container():
        senha = st.text_input("🔐 Chave de Acesso:", type="password")
        if st.button("Entrar"):
            if senha == "sandro2026":
                st.session_state['auth'] = True
                st.rerun()
    st.stop()

# 3. Radar de Ativos (Sidebar)
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_input = st.text_input("Digite o Ticker:", "").upper()
    st.divider()
    st.subheader("💡 Sugestões do Dia")
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CMIG4"]
    escolha = st.radio("Selecione:", ["Nenhuma"] + sugestoes)

ticker_final = ticker_input if ticker_input else (escolha if escolha != "Nenhuma" else "")

if ticker_final:
    # Lógica Anti-Erro de Ticker
    simbolo_limpo = ticker_final.replace(".SA", "")
    
    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA")
        if st.button("✨ Gerar Análise Profissional"):
            try:
                key = st.secrets["GOOGLE_API_KEY"]
                # Rota Direta v1 (A mais estável)
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": f"Analise rápida de {ticker_final} para dividendos."}]}]}
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    st.success("Análise Concluída:")
                    st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                else:
                    st.error(f"Erro {res.status_code}: Verifique sua API Key.")
            except:
                st.warning("Conexão com a IA temporariamente indisponível.")

    with col2:
        st.subheader(f"📊 Histórico: {ticker_final}")
        try:
            # Tenta buscar com e sem .SA para evitar o erro de 'timezone'
            data = yf.Ticker(f"{simbolo_limpo}.SA")
            divs = data.dividends
            if divs.empty:
                data = yf.Ticker(simbolo_limpo)
                divs = data.dividends
            
            if not divs.empty:
                df = divs.tail(15).to_frame().reset_index()
                df.columns = ['Data', 'Valor']
                
                # Gráfico de Barras Premium (Altair)
                chart = alt.Chart(df).mark_bar(size=30, color='#008cff').encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Valor:Q', title='Valor (R$)'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)
                
                # Detalhamento
                st.subheader("📋 Detalhamento (Precisão: 0.001)")
                df_tab = df.sort_values(by='Data', ascending=False)
                df_tab['Valor'] = df_tab['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_tab, use_container_width=True, hide_index=True)
            else:
                st.warning(f"Não encontramos dividendos recentes para {ticker_final}.")
        except Exception as e:
            st.error("Erro na comunicação com a B3. Tente outro ticker.")

st.divider()
st.caption("InvestSmart Pro v24.0 | 2026")
