import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import altair as alt

# 1. Configuração e Estilo
st.set_page_config(page_title="InvestSmart Pro | Cripto Scanner", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso:", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. RADAR DE CRIPTO ---
with st.sidebar:
    st.header("⚡ Cripto Scanner")
    # Moedas com foco em liquidez e staking (renda passiva cripto)
    criptos_radar = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD"]
    moeda_selecionada = st.selectbox("Escolha para Monitorar:", criptos_radar)
    
    st.divider()
    st.subheader("🤖 Configuração do Robô")
    alerta_vol = st.slider("Alerta de Volatilidade (%)", 1.0, 10.0, 3.0)

# --- 4. MOTOR DE BUSCA (Rota Especializada para Cripto) ---
def scanner_cripto(ticker):
    try:
        data = yf.Ticker(ticker)
        # Busca dados de 1 hora com intervalos de 15 minutos para ser "tempo real"
        hist = data.history(period="1d", interval="15m")
        if not hist.empty:
            return data, hist
        return None, None
    except:
        return None, None

# --- INTERFACE ---
st.title("🏛️ InvestSmart Pro | Scanner de Cripto")

if moeda_selecionada:
    obj, hist = scanner_cripto(moeda_selecionada)
    
    if hist is not None:
        col1, col2 = st.columns([1, 1.5], gap="large")
        
        with col1:
            st.subheader("🤖 Mentor IA (Sentinela Cripto)")
            atual = hist['Close'].iloc[-1]
            anterior = hist['Open'].iloc[0]
            var = ((atual / anterior) - 1) * 100
            
            # Sinalizador de Cor
            cor = "normal" if abs(var) < alerta_vol else "inverse"
            st.metric(f"Preço {moeda_selecionada}", f"US$ {atual:,.2f}", f"{var:.2f}%", delta_color=cor)
            
            if abs(var) > alerta_vol:
                st.warning(f"🚨 ALERTA: {moeda_selecionada} rompeu o limite de {alerta_vol}%!")
            
            if st.button("✨ Analisar Ciclo"):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    prompt = f"O {moeda_selecionada} variou {var:.2f}% em 24h. Isso indica oportunidade ou risco?"
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
                    st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                except:
                    st.error("Erro de comunicação com o cérebro da IA.")

        with col2:
            st.subheader("📊 Movimentação de Curto Prazo")
            # Gráfico de Área para Cripto (Fica mais profissional)
            chart_data = hist.reset_index()
            chart = alt.Chart(chart_data).mark_area(
                line={'color':'#008cff'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='white', offset=0),
                           alt.GradientStop(color='#008cff', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(x='Datetime:T', y='Close:Q').properties(height=350)
            st.altair_chart(chart, use_container_width=True)
    else:
        st.error("Falha na conexão com a Exchange. Tentando reconectar...")

st.caption("InvestSmart Pro v31.0 | Scanner Cripto 24/7")
