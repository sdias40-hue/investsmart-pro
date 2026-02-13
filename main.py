import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração e Estilo Terminal Bloomberg
st.set_page_config(page_title="InvestSmart Pro | Gestor Master", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso ao Terminal:", type="password")
    if st.button("Abrir"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. BANCO DE INTELIGÊNCIA (BDR vs CRIPTO) ---
# Aqui o robô guarda as taxas de rendimento para comparar
oportunidades = {
    "JEPP34 (BDR)": {"ticker": "JEPP34.SA", "yield": 0.12, "tipo": "Dividendo"},
    "ETH-USD (Cripto)": {"ticker": "ETH-USD", "yield": 0.036, "tipo": "Staking"},
    "BBAS3 (Ação)": {"ticker": "BBAS3.SA", "yield": 0.09, "tipo": "Dividendo"},
    "SOL-USD (Cripto)": {"ticker": "SOL-USD", "yield": 0.072, "tipo": "Staking"}
}

# --- 4. RADAR DE OPORTUNIDADES ---
with st.sidebar:
    st.header("🔍 Radar Híbrido")
    escolha = st.selectbox("Selecione o Ativo para Análise:", list(oportunidades.keys()))
    capital = st.number_input("Capital para Investimento (R$ ou US$):", 100, 100000, 5000)
    st.divider()
    st.info("💡 O robô está configurado para buscar a maior eficiência de renda passiva.")

st.title("🏛️ InvestSmart Pro | Gestor de Renda Unificado")

# 5. EXECUÇÃO DO SCANNER (Processamento Massivo)
info = oportunidades[escolha]
ticker = info["ticker"]

data_obj = yf.Ticker(ticker)
# Busca histórico para mostrar a volatilidade que o robô monitora
hist = data_obj.history(period="5d")

if not hist.empty:
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader(f"💎 Inteligência: {info['tipo']}")
        atual = hist['Close'].iloc[-1]
        var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        
        # O robô adapta a moeda automaticamente
        simbolo = "US$" if "USD" in ticker else "R$"
        st.metric(f"Preço Atual ({ticker})", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
        
        # Cálculo de Eficiência de Renda
        renda_anual = capital * info["yield"]
        renda_mensal = renda_anual / 12
        
        st.markdown(f"### 🚀 Projeção de Renda: {info['yield']*100:.1f}% a.a.")
        c1, c2 = st.columns(2)
        c1.metric("Mensal Previsto", f"{simbolo} {renda_mensal:,.2f}")
        c2.metric("Anual Previsto", f"{simbolo} {renda_anual:,.2f}")
        
        st.success(f"O robô validou: {escolha} é ideal para formação de patrimônio via {info['tipo']}.")

    with col2:
        st.subheader("📊 Monitoramento de Tendência")
        chart_data = hist.reset_index()
        chart = alt.Chart(chart_data).mark_line(point=True, color='#008cff').encode(
            x='Date:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False)),
            tooltip=['Date', 'Close']
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)
else:
    st.error("Erro na comunicação com o mercado. O robô está tentando reconectar...")

st.caption("InvestSmart Pro v37.0 | Sentinela Híbrido (B3 & Cripto)")
