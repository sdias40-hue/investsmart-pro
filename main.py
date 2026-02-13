import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração Estrita
st.set_page_config(page_title="InvestSmart Pro | Sentinela", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. A PONTE DEFINITIVA (Rota de Emergência) ---
def mentor_ia_definitivo(ticker, var, preco):
    try:
        if "GOOGLE_API_KEY" not in st.secrets:
            return "Erro: Chave API não configurada no Secrets do Streamlit."
            
        key = st.secrets["GOOGLE_API_KEY"]
        # Rota mais compatível com o Streamlit Cloud
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        
        headers = {'Content-Type': 'application/json'}
        # Prompt enxuto para evitar que a conexão caia por excesso de dados
        prompt = f"Analise rápida: {ticker} a US$ {preco:,.2f} ({var:.2f}%). Estratégia de renda?"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"O cérebro da IA retornou erro {response.status_code}. Verifique a API Key."
    except Exception as e:
        return "Conexão interrompida. O robô está recalibrando."

# --- 4. SCANNER REAL-TIME ---
with st.sidebar:
    st.header("⚡ Cripto Scanner")
    moeda = st.selectbox("Escolha a Moeda:", ["BNB-USD", "SOL-USD", "BTC-USD", "ETH-USD"])
    alerta_vol = st.slider("Alerta Volatilidade (%)", 1.0, 10.0, 3.0)

st.title("🏛️ InvestSmart Pro | Scanner Sentinela")

# Busca de dados limpa
ticker_data = yf.Ticker(moeda)
hist = ticker_data.history(period="1d", interval="15m")

if not hist.empty:
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("🤖 Mentor IA (Status: Ativo)")
        # Preço focado no seu último print do BNB-USD
        atual = hist['Close'].iloc[-1]
        var = ((atual / hist['Open'].iloc[0]) - 1) * 100
        st.metric(f"Preço {moeda}", f"US$ {atual:,.2f}", f"{var:.2f}%")
        
        if st.button("✨ Executar Análise de Renda"):
            with st.spinner("Processando dados massivos..."):
                resultado = mentor_ia_definitivo(moeda, var, atual)
                st.info(resultado)

    with col2:
        st.subheader("📊 Movimentação Real-Time")
        chart_data = hist.reset_index()
        chart = alt.Chart(chart_data).mark_area(line={'color':'#008cff'}, color='#008cff33').encode(
            x='Datetime:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False))
        ).properties(height=380)
        st.altair_chart(chart, use_container_width=True)
else:
    st.error("Erro na ponte de dados. Tente atualizar a página.")
