import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração e Estilo
st.set_page_config(page_title="InvestSmart Pro | Visão Total", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. BANCO DE DADOS DE STAKING (Inteligência do Robô) ---
yield_staking = {"SOL-USD": 0.07, "ETH-USD": 0.035, "BNB-USD": 0.025, "ADA-USD": 0.03}

# --- 4. RADAR MASTER ---
with st.sidebar:
    st.header("🔍 Radar Master")
    ticker_input = st.text_input("Ticker (Ex: BBAS3, SOL-USD, JEPP34):", "").upper()
    st.divider()
    sugestao = st.selectbox("Sugestões:", ["", "BBAS3", "TAEE11", "JEPP34", "SOL-USD", "ETH-USD"])
    ticker_final = ticker_input if ticker_input else sugestao

# --- 5. MOTOR DE BUSCA ROBUSTO ---
def buscar_dados(t):
    try:
        rotas = [f"{t}.SA", t, t.replace(".SA", "")]
        for r in rotas:
            obj = yf.Ticker(r)
            hist = obj.history(period="5d")
            if not hist.empty:
                return obj, hist
        return None, None
    except:
        return None, None

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Oportunidades")

if ticker_final:
    obj, hist = buscar_dados(ticker_final)
    
    if hist is not None:
        col1, col2 = st.columns([1, 1.4], gap="large")
        
        with col1:
            st.subheader("🤖 Sentinela de Inteligência")
            atual = hist['Close'].iloc[-1]
            var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
            simbolo = "US$" if "USD" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            # --- BLOCO A: AÇÕES/BDRs (Dividendos) ---
            if "USD" not in ticker_final:
                divs = obj.dividends
                if not divs.empty:
                    pago_ano = divs.tail(4).sum()
                    preco_justo = pago_ano / 0.06
                    st.write(f"### 🎯 Preço Justo (Bazin): {simbolo} {preco_justo:,.2f}")
                    if atual < preco_justo:
                        st.success("💎 Abaixo do preço justo. Oportunidade!")
                    if var < -1.5:
                        st.error("🚨 QUEDA DE PREÇO BOA PARA COMPRAR!")
                else:
                    st.info("Buscando proventos oficiais...")

            # --- BLOCO B: CRIPTO (Staking) ---
            else:
                yield_est = yield_staking.get(ticker_final, 0)
                if yield_est > 0:
                    st.write(f"### ⛏️ Staking Yield: {yield_est*100:.1f}% a.a.")
                    st.success(f"Este ativo gera renda passiva via validação de rede.")
                    if var < -3.0:
                        st.error("🚨 VOLATILIDADE ALTA: Ótimo ponto para Staking!")

        with col2:
            st.subheader("📊 Gráfico de Tendência")
            chart_data = hist.reset_index()
            chart = alt.Chart(chart_data).mark_line(point=True, color='#008cff').encode(
                x='Date:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False))
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)
            
            # Tabela de Proventos/Staking (Abaixo do Gráfico)
            if "USD" not in ticker_final:
                st.subheader("📋 Últimos Dividendos")
                divs_df = obj.dividends.tail(10).to_frame().reset_index()
                if not divs_df.empty:
                    divs_df.columns = ['Data', 'Valor']
                    st.dataframe(divs_df.sort_values(by='Data', ascending=False), use_container_width=True)
    else:
        st.error(f"Erro na conexão com {ticker_final}. O robô está recalibrando a rota.")
else:
    st.info("👋 Radar aguardando comando. Digite um ativo para iniciar o processamento massivo.")
