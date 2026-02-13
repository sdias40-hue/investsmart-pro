import streamlit as st
import yfinance as yf
import requests
import json
import pandas as pd
import altair as alt

# 1. Setup Premium
st.set_page_config(page_title="InvestSmart Pro | O Bote", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login de Segurança
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. RADAR DE CRIPTO ---
with st.sidebar:
    st.header("⚡ Cripto Scanner")
    moeda = st.selectbox("Moeda:", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD"])
    st.divider()
    alerta_vol = st.slider("Alerta Volatilidade (%)", 1.0, 10.0, 3.0)

# --- 4. O BOTE: CONEXÃO DIRETA COM A IA ---
def mentor_ia_comunicar(ticker, var, preco):
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        # ROTA DIRETA v1: Sem intermediários para evitar erro 404
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
        
        headers = {'Content-Type': 'application/json'}
        prompt = f"Aja como um investidor experiente. O {ticker} está custando US$ {preco:,.2f} com variação de {var:.2f}%. Dê uma dica rápida de formação de renda."
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro de Conexão {response.status_code}. Verifique sua chave no Secrets."
    except Exception as e:
        return f"Erro Técnico: {str(e)}"

# --- 5. INTERFACE ---
st.title("🏛️ InvestSmart Pro | Scanner Sentinela")

# Busca de dados
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
            with st.spinner("O Mentor está processando os dados massivos..."):
                analise = mentor_ia_comunicar(moeda, var, atual)
                st.info(analise)

    with col2:
        st.subheader("📊 Movimentação Real-Time")
        # Gráfico que você aprovou
        chart_data = hist.reset_index()
        chart = alt.Chart(chart_data).mark_area(line={'color':'#008cff'}, color='#008cff33').encode(
            x='Datetime:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False))
        ).properties(height=380)
        st.altair_chart(chart, use_container_width=True)

else:
    st.error("Falha na ponte de dados. Tentando nova rota...")

st.caption("InvestSmart Pro v32.0 | Conexão Mestra Estabelecida")
