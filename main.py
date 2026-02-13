import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração e Estilo
st.set_page_config(page_title="InvestSmart Pro | Sentinela", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. FUNÇÃO MESTRA (Com redundância de versão e tratamento de erro) ---
def mentor_ia_stream(ticker, var, preco):
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        # Tentamos a rota estável v1 primeiro desta vez
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
        
        headers = {'Content-Type': 'application/json'}
        prompt = f"Analise massiva: O ativo {ticker} está a US$ {preco:,.2f} ({var:.2f}%). Com foco em dividendos e renda, qual a estratégia agressiva para agora?"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # Se a v1 der 404, tentamos a v1beta como última chance
            url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            response = requests.post(url_beta, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            return f"Erro de comunicação ({response.status_code}). O cérebro da IA está em manutenção."
    except Exception as e:
        return f"Erro de Conexão: O robô está offline."

# --- 4. SCANNER REAL-TIME ---
with st.sidebar:
    st.header("⚡ Cripto Scanner")
    moeda = st.selectbox("Escolha a Moeda:", ["SOL-USD", "BTC-USD", "ETH-USD", "BNB-USD"])
    alerta_vol = st.slider("Alerta Volatilidade (%)", 1.0, 10.0, 3.0)

st.title("🏛️ InvestSmart Pro | Scanner Sentinela")

# Busca de dados com zoom no preço atual para ser competitivo
data_obj = yf.Ticker(moeda)
hist = data_obj.history(period="1d", interval="15m")

if not hist.empty:
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("🤖 Mentor IA (Status: Ativo)")
        atual = hist['Close'].iloc[-1]
        # Cálculo de variação real baseado no preço de US$ 84.50 (SOL) do seu print
        var = ((atual / hist['Open'].iloc[0]) - 1) * 100
        st.metric(f"Preço {moeda}", f"US$ {atual:,.2f}", f"{var:.2f}%")
        
        if st.button("✨ Iniciar Análise Massiva"):
            placeholder = st.empty()
            with st.spinner("O robô está processando tendências que humanos não veem..."):
                resultado = mentor_ia_stream(moeda, var, atual)
                placeholder.info(resultado)

    with col2:
        st.subheader("📊 Movimentação Real-Time")
        chart_data = hist.reset_index()
        chart = alt.Chart(chart_data).mark_area(line={'color':'#008cff'}, color='#008cff33').encode(
            x='Datetime:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False))
        ).properties(height=380)
        st.altair_chart(chart, use_container_width=True)
else:
    st.error("Erro na ponte de dados. Verifique a conexão com a Exchange.")
