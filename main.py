import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Configuração e Estilo (Mantendo o visual que você gostou)
st.set_page_config(page_title="InvestSmart Pro | O Bote Final", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. FUNÇÃO DE IA COM PONTE DE REDUNDÂNCIA ---
def chamar_mentor_ia(ticker, var, preco):
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        headers = {'Content-Type': 'application/json'}
        prompt = f"O ativo {ticker} está a US$ {preco:,.2f} com variação de {var:.2f}%. Dê um insight curto de investimento."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        # TESTA ROTA 1 (v1beta)
        url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        res = requests.post(url_beta, headers=headers, data=json.dumps(payload), timeout=10)
        
        if res.status_code != 200:
            # TESTA ROTA 2 (v1 oficial) se a primeira falhar
            url_v1 = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
            res = requests.post(url_v1, headers=headers, data=json.dumps(payload), timeout=10)
            
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro de Autorização ({res.status_code}). Verifique se sua chave API está ativa no Google AI Studio."
    except Exception as e:
        return f"Erro de Rede: {str(e)}"

# --- 4. INTERFACE E SCANNER ---
with st.sidebar:
    st.header("⚡ Cripto Scanner")
    moeda = st.selectbox("Escolha a Moeda:", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD"])
    alerta_vol = st.slider("Alerta Volatilidade (%)", 1.0, 10.0, 3.0)

st.title("🏛️ InvestSmart Pro | Scanner Sentinela")

# Busca de dados frescos
data_obj = yf.Ticker(moeda)
hist = data_obj.history(period="1d", interval="15m")

if not hist.empty:
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("🤖 Mentor IA (Status: Ativo)")
        atual = hist['Close'].iloc[-1]
        var = ((atual / hist['Open'].iloc[0]) - 1) * 100
        st.metric(f"Preço {moeda}", f"US$ {atual:,.2f}", f"{var:.2f}%")
        
        if st.button("✨ Solicitar Insight do Mentor"):
            with st.spinner("Conectando ao cérebro do robô..."):
                resultado = chamar_mentor_ia(moeda, var, atual)
                st.info(resultado)

    with col2:
        st.subheader("📊 Movimentação Real-Time")
        chart_data = hist.reset_index()
        chart = alt.Chart(chart_data).mark_area(line={'color':'#008cff'}, color='#008cff33').encode(
            x='Datetime:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False))
        ).properties(height=380)
        st.altair_chart(chart, use_container_width=True)
else:
    st.error("Erro na ponte de dados com a Exchange.")
