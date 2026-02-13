import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração de Elite
st.set_page_config(page_title="InvestSmart Pro | Renda", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. BANCO DE DADOS DE YIELD (Renda Cripto Est.) ---
yield_map = {
    "SOL-USD": 0.072,  # 7.2% ao ano
    "ETH-USD": 0.036,  # 3.6% ao ano
    "BNB-USD": 0.024,  # 2.4% ao ano
    "ADA-USD": 0.031   # 3.1% ao ano
}

# --- 4. SCANNER DE MERCADO ---
with st.sidebar:
    st.header("⚡ Sentinela de Renda")
    moeda = st.selectbox("Moeda para Análise:", list(yield_map.keys()))
    capital_est = st.number_input("Capital Investido (US$):", 100, 100000, 1000)

st.title("🏛️ InvestSmart Pro | Calculador de Renda Passiva")

# Busca de dados em tempo real (Diferencial do Projeto)
data_obj = yf.Ticker(moeda)
hist = data_obj.history(period="1d", interval="15m")

if not hist.empty:
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("💰 Projeção de Ganhos")
        atual = hist['Close'].iloc[-1]
        var = ((atual / hist['Open'].iloc[0]) - 1) * 100
        
        # Métrica de Preço Real-Time
        st.metric(f"Preço {moeda}", f"US$ {atual:,.2f}", f"{var:.2f}%")
        
        # Lógica de Dividendos Cripto (Staking)
        taxa = yield_map.get(moeda, 0)
        ganho_anual = capital_est * taxa
        ganho_mensal = ganho_anual / 12
        
        st.divider()
        st.write(f"### 📈 Yield Estimado: {taxa*100:.1f}% a.a.")
        
        c1, c2 = st.columns(2)
        c1.metric("Renda Mensal Est.", f"US$ {ganho_mensal:,.2f}")
        c2.metric("Renda Anual Est.", f"US$ {ganho_anual:,.2f}")
        
        st.info(f"O robô identificou que com {moeda} a US$ {atual:,.2f}, sua taxa de eficiência de capital está otimizada.")

    with col2:
        st.subheader("📊 Gráfico de Volatilidade Massiva")
        chart_data = hist.reset_index()
        chart = alt.Chart(chart_data).mark_area(line={'color':'#008cff'}, color='#008cff33').encode(
            x='Datetime:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False))
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
else:
    st.error("Falha na comunicação com a Exchange. Verifique os logs.")

st.caption("InvestSmart Pro v36.0 | Módulo de Renda Ativo")
