import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração de Elite
st.set_page_config(page_title="InvestSmart Pro | Dividendos", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. RADAR MASTER ---
with st.sidebar:
    st.header("🔍 Radar Master")
    ticker_input = st.text_input("Ticker (Ex: JEPP34, TAEE11, BBAS3):", "").upper()
    st.divider()
    sugestao = st.selectbox("Sugestões de Renda:", ["", "JEPP34", "TAEE11", "BBAS3", "VULC3", "SOL-USD"])
    ticker_final = ticker_input if ticker_input else sugestao

# --- 4. MOTOR DE BUSCA COM TRIPLA TENTATIVA (Correção para BDR) ---
def buscar_dados_completos(t):
    try:
        # Tenta rotas: 1. Com .SA | 2. Puro | 3. Sem sufixo (BDR/Cripto)
        rotas = [f"{t}.SA", t, t.replace(".SA", "")]
        for r in rotas:
            obj = yf.Ticker(r)
            # Busca histórico curto para validar a conexão
            h = obj.history(period="5d")
            if not h.empty:
                # Se achou o preço, busca os dividendos
                d = obj.dividends
                return obj, h, d
        return None, None, None
    except:
        return None, None, None

# --- INTERFACE ---
st.title("🏛️ InvestSmart Pro | Gestão de Oportunidades")

if ticker_final:
    obj, hist, divs = buscar_dados_completos(ticker_final)
    
    if hist is not None:
        col1, col2 = st.columns([1, 1.4], gap="large")
        
        with col1:
            st.subheader("🤖 Sentinela de Preço")
            atual = hist['Close'].iloc[-1]
            var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
            simbolo = "US$" if "USD" in ticker_final else "R$"
            st.metric(f"Preço Atual ({ticker_final})", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            # Lógica de Preço Justo (Baseada no sucesso da TAEE11: R$ 53.82)
            if divs is not None and not divs.empty:
                pago_ano = divs.tail(4).sum()
                if pago_ano > 0:
                    preco_justo = pago_ano / 0.06
                    st.write(f"### 🎯 Preço Justo (Bazin): {simbolo} {preco_justo:,.2f}")
                    if atual < preco_justo:
                        st.success("💎 Ativo abaixo do preço justo. Oportunidade!")
                    else:
                        st.warning("⚠️ Ativo acima do preço justo.")
            
            if var < -1.5:
                st.error("🚨 QUEDA DE PREÇO BOA PARA COMPRAR!")

        with col2:
            st.subheader(f"📊 Histórico de Proventos: {ticker_final}")
            if divs is not None and not divs.empty:
                df_divs = divs.tail(15).to_frame().reset_index()
                df_divs.columns = ['Data', 'Valor']
                # Gráfico de Barras Separadas Profissional
                chart = alt.Chart(df_divs).mark_bar(size=25, color='#008cff').encode(
                    x='Data:T', y='Valor:Q'
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
                
                st.subheader("📋 Detalhamento (Precisão: 0.001)")
                df_tab = df_divs.sort_values(by='Data', ascending=False)
                df_tab['Valor'] = df_tab['Valor'].map('{:,.3f}'.format)
                st.dataframe(df_tab, use_container_width=True, hide_index=True)
            else:
                st.info("Aguardando confirmação de dividendos oficiais para este ticker.")
    else:
        st.error(f"Erro na comunicação com {ticker_final}. Verifique o código no Yahoo Finance.")
else:
    st.info("👋 Digite um Ticker ou selecione uma Sugestão ao lado.")
