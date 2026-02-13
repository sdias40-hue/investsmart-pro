import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração e Estilo
st.set_page_config(page_title="InvestSmart Pro | Analista", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA COM TRIPLA TENTATIVA (Correção BDR) ---
def buscar_dados_completos(t):
    try:
        rotas = [f"{t}.SA", t, t.replace(".SA", "")]
        for r in rotas:
            obj = yf.Ticker(r)
            # Buscamos 60 dias para calcular as Médias Móveis de tendência
            h = obj.history(period="60d")
            if not h.empty:
                return obj, h
        return None, None
    except:
        return None, None

# --- 4. RADAR MASTER ---
with st.sidebar:
    st.header("🔍 Radar Master")
    ticker_input = st.text_input("Ticker (Ex: MSCD34, PETR4, SOL-USD):", "").upper()
    st.divider()
    sugestao = st.selectbox("Sugestões:", ["", "MSCD34", "TAEE11", "BBAS3", "SOL-USD"])
    ticker_final = ticker_input if ticker_input else sugestao

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestor de Oportunidades")

if ticker_final:
    obj, hist = buscar_dados_completos(ticker_final)
    
    if hist is not None:
        # CÁLCULO DE TENDÊNCIA (Média Móvel de 9 e 21 dias)
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        hist['MA21'] = hist['Close'].rolling(window=21).mean()
        
        col1, col2 = st.columns([1, 1.4], gap="large")
        
        with col1:
            st.subheader("🤖 Sentinela de Inteligência")
            atual = hist['Close'].iloc[-1]
            ma9_atual = hist['MA9'].iloc[-1]
            var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
            
            st.metric(f"Preço {ticker_final}", f"R$ {atual:,.2f}", f"{var:.2f}%")
            
            # --- ANÁLISE DE TENDÊNCIA GRÁFICA ---
            st.divider()
            st.write("### 📈 Análise de Tendência")
            if atual > ma9_atual:
                st.success("🔥 TENDÊNCIA DE ALTA: Preço acima da média rápida.")
            else:
                st.error("📉 TENDÊNCIA DE BAIXA: Preço abaixo da média rápida.")
            
            # Alerta de oportunidade que você aprovou
            if var < -1.5:
                st.warning("🚨 QUEDA DE PREÇO BOA PARA COMPRAR!")

        with col2:
            st.subheader("📊 Gráfico com Médias Móveis")
            # Preparando dados para o gráfico
            chart_data = hist.tail(30).reset_index()
            
            # Linha de Preço
            base = alt.Chart(chart_data).encode(x='Date:T')
            line_price = base.mark_line(color='#008cff', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
            
            # Linha da Média Móvel (MA9)
            line_ma9 = base.mark_line(color='#ffaa00', strokeDash=[5,5]).encode(y='MA9:Q')
            
            st.altair_chart(line_price + line_ma9, use_container_width=True)
            st.caption("🔵 Preço Atual | 🟠 Média Móvel (Tendência)")
            
    else:
        st.error(f"Erro na conexão com {ticker_final}. O robô está recalibrando.")
else:
    st.info("👋 Use o Radar ao lado para iniciar a análise de tendência massiva.")
