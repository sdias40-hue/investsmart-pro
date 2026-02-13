import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import altair as alt

# 1. Layout e Visual Premium (Recuperando a Identidade)
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="column"] { padding: 0 30px !important; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso:", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- 3. RECUPERANDO O RADAR E SUGESTÕES (Funcionalidade Reativada) ---
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_manual = st.text_input("Digite o Ticker (Ex: MXRF11):", "").upper()
    
    st.divider()
    st.subheader("💡 Top 5 Fundamentalistas")
    # Voltando com a lista que você aprovou
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CMIG4"]
    escolha_sugestao = st.radio("Selecione para análise rápida:", ["Nenhuma"] + sugestoes)
    
    ticker_final = ticker_manual if ticker_manual else (escolha_sugestao if escolha_sugestao != "Nenhuma" else "PETR4")

# --- 4. CONECTOR B3 COM REDUNDÂNCIA (Diferencial Técnico) ---
@st.cache_data(ttl=300)
def obter_proventos(t):
    try:
        # Tenta primeira rota (com .SA)
        simbolo = f"{t}.SA" if ".SA" not in t else t
        ticket_obj = yf.Ticker(simbolo)
        divs = ticket_obj.dividends
        if divs.empty:
            # Tenta segunda rota (sem .SA para BDRs)
            ticket_obj = yf.Ticker(t.replace(".SA", ""))
            divs = ticket_obj.dividends
        return divs
    except:
        return pd.Series()

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Ativos")

col1, col2 = st.columns([1, 1.4], gap="large")

with col1:
    st.subheader("🤖 Mentor IA (Análise CNPI)")
    if st.button("✨ Solicitar Análise"):
        with st.spinner("Processando..."):
            try:
                key = st.secrets["GOOGLE_API_KEY"]
                # Forçando Rota v1 para matar o Erro 404 de vez
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                payload = {"contents": [{"parts": [{"text": f"Analise rápida de dividendos para {ticker_final}."}]}]}
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                else:
                    st.error("Erro 404 na IA. Verifique sua chave API.")
            except:
                st.warning("IA temporariamente indisponível.")

with col2:
    st.subheader(f"📊 Dividendos: {ticker_final}")
    divs_data = obter_proventos(ticker_final)
    
    if not divs_data.empty:
        df = divs_data.tail(15).to_frame().reset_index()
        df.columns = ['Data', 'Valor']
        # Gráfico de Barras Separadas (O que você mais gostou)
        chart = alt.Chart(df).mark_bar(size=28, color='#008cff').encode(
            x='Data:T', y='Valor:Q', tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
        ).properties(height=380)
        st.altair_chart(chart, use_container_width=True)
        
        st.subheader("📋 Detalhamento (Precisão: 0.001)")
        df_tab = df.sort_values(by='Data', ascending=False)
        df_tab['Valor'] = df_tab['Valor'].map('{:,.3f}'.format)
        st.dataframe(df_tab, use_container_width=True, hide_index=True)
    else:
        st.warning(f"Aguardando conexão com a B3 para {ticker_final}. Tente CMIG4.")

st.divider()
st.caption("InvestSmart Pro v26.0 | Resgate de Funcionalidades")
