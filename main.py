import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração de Página
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")

# Estilo para visual profissional e limpo
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; height: 3em; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e3141,#2e3141); color: white; }
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

# Sidebar com Radar de Ativos
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    # Campo vazio para o usuário preencher
    ticker_input = st.text_input("Digite o Ticker desejado:", "").upper()
    
    st.write("---")
    st.subheader("💡 Sugestões do Radar")
    st.caption("Top 5 Oportunidades (DY/Resiliência):")
    # Lista de sugestões como texto para o usuário se inspirar
    st.info("1. JEPP34 (BDR Dividendos)\n2. BBAS3 (Banco do Brasil)\n3. TAEE11 (Taesa)\n4. PETR4 (Petrobras)\n5. CPLE6 (Copel)")
    
    st.divider()
    st.caption("InvestSmart Pro v16.0 | 2026")

if ticker_input:
    ticker = f"{ticker_input}.SA" if ".SA" not in ticker_input else ticker_input
    
    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.subheader("🤖 Mentor IA (Análise Fundamentalista)")
        if st.button("✨ Gerar Análise"):
            with st.spinner("Analisando mercado..."):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"Analise brevemente {ticker} focando em dividendos."}]}]}
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        st.info(response.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.warning("IA em manutenção. Use os dados técnicos ao lado.")
                except:
                    st.error("Erro na conexão com o Mentor.")

    with col2:
        st.subheader(f"📊 Histórico de Proventos: {ticker_input}")
        try:
            acao = yf.Ticker(ticker)
            divs = acao.dividendos if hasattr(acao, 'dividendos') else acao.dividends
            
            if not divs.empty:
                df_divs = divs.tail(15).to_frame().reset_index()
                df_divs.columns = ['Data', 'Valor']
                
                # Gráfico com barras grossas (Altair) como no exemplo profissional
                chart = alt.Chart(df_divs).mark_bar(size=35, color='#008cff').encode(
                    x=alt.X('Data:T', title='Data do Pagamento'),
                    y=alt.Y('Valor:Q', title='Valor (R$)'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=400).configure_axis(grid=False)
                
                st.altair_chart(chart, use_container_width=True)
                
                # Detalhamento com 3 casas decimais
                st.subheader("📋 Detalhamento (Precisão de 3 Casas)")
                df_display = df_divs.copy()
                df_display = df_display.sort_values(by='Data', ascending=False)
                # Formatação para 3 casas decimais
                df_display['Valor'] = df_display['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum dividendo encontrado para este ativo.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
else:
    st.info("👋 Digite um Ticker no Radar à esquerda para iniciar a análise.")

st.divider()
st.caption("⚠️ Dados: Yahoo Finance | Precisão: 0.001 | InvestSmart Pro 2026")
