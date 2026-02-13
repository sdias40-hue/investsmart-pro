import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração de Terminal Profissional
st.set_page_config(page_title="InvestSmart Pro | Inteligência", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. RADAR DE BUSCA LIVRE (Diferencial do Projeto) ---
with st.sidebar:
    st.header("🔍 Radar Master")
    # Agora você pode digitar qualquer ticker aqui
    ticker_input = st.text_input("Digite qualquer Ticker (Ex: JEPP34, PETR4, BTC-USD):", "").upper()
    
    st.divider()
    st.subheader("💡 Sugestões de Renda")
    sugestao = st.selectbox("Ou selecione da lista:", ["", "JEPP34", "BBAS3", "TAEE11", "SOL-USD", "ETH-USD"])
    
    ticker_final = ticker_input if ticker_input else sugestao

# --- 4. FUNÇÃO DE BUSCA E INTELIGÊNCIA ---
def analisar_oportunidade(t):
    try:
        # Tenta rotas alternativas para evitar o Erro 404
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="2d")
            if not hist.empty:
                return obj, hist
        return None, None
    except:
        return None, None

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestor de Oportunidades")

if ticker_final:
    obj, historico = analisar_oportunidade(ticker_final)
    
    if historico is not None:
        col1, col2 = st.columns([1, 1.4], gap="large")
        
        with col1:
            st.subheader("🤖 Sentinela: Avaliação de Preço")
            atual = historico['Close'].iloc[-1]
            var = ((atual / historico['Close'].iloc[-2]) - 1) * 100
            
            # 1. Valor Atual e Variação
            simbolo = "US$" if "USD" in ticker_final else "R$"
            st.metric(f"Preço Atual ({ticker_final})", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            # 2. Lógica de Preço Justo (Exemplo Didático de Bazin para Ações)
            st.divider()
            if "USD" not in ticker_final:
                # Simulação: Robô busca dividendos do último ano
                divs = obj.dividends
                if not divs.empty:
                    pago_ano = divs.tail(4).sum()
                    preco_justo = pago_ano / 0.06 # Rendimento de 6%
                    st.write(f"### 🎯 Preço Justo (Bazin): {simbolo} {preco_justo:,.2f}")
                    
                    if atual < preco_justo:
                        st.success("💎 Ativo abaixo do preço justo. Oportunidade!")
                    else:
                        st.warning("⚠️ Ativo acima do preço justo. Cuidado.")
                
            # 3. Alerta de Queda
            if var < -1.5:
                st.error("🚨 QUEDA DE PREÇO BOA PARA COMPRAR!")
            elif var > 1.5:
                st.info("🚀 Ativo em forte alta. Monitore o RSI.")

        with col2:
            st.subheader("📊 Histórico e Tendência")
            chart_data = historico.reset_index()
            chart = alt.Chart(chart_data).mark_line(point=True, color='#008cff').encode(
                x='Date:T', y=alt.Y('Close:Q', scale=alt.Scale(zero=False))
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)
    else:
        st.error(f"Erro na comunicação com {ticker_final}. Tente outro ticker ou verifique o código.")
else:
    st.info("👋 Use o Radar ao lado para analisar qualquer ativo da B3 ou Cripto.")

st.caption("InvestSmart Pro v38.0 | Sentinela de Oportunidades")
