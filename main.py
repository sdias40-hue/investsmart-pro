import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import altair as alt

# 1. Configuração e Estilo Premium
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")
st.markdown("""<style>.main { background-color: #0e1117; color: white; } [data-testid="column"] { padding: 0 20px !important; }</style>""", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso:", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. RADAR E MONITORAMENTO (Ticker Inicial Vazio) ---
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    # Campo limpo para você digitar qualquer coisa (Ação, Moeda, BDR)
    ticker_input = st.text_input("Buscar (Ex: BTC-USD, PETR4, JEPP34):", "").upper()
    
    st.divider()
    st.subheader("💡 Top 5 Fundamentalistas")
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CMIG4"]
    escolha = st.radio("Destaques do Dia:", ["Nenhuma"] + sugestoes)
    
    ticker_final = ticker_input if ticker_input else (escolha if escolha != "Nenhuma" else "")

# --- 4. FUNÇÃO DE DADOS PUROS (Causa Raiz da Estabilidade) ---
def buscar_dados_seguros(t):
    try:
        # Tenta rotas alternativas para garantir a comunicação
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            ticker_obj = yf.Ticker(s)
            # Buscamos apenas o histórico de preço (Diferencial do Projeto)
            hist = ticker_obj.history(period="5d")
            if not hist.empty:
                return ticker_obj, hist
        return None, None
    except:
        return None, None

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Ativos")

if ticker_final:
    obj, historico = buscar_dados_seguros(ticker_final)
    
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA (Sentinela)")
        if historico is not None:
            # Monitoramento em Tempo Real
            atual = historico['Close'].iloc[-1]
            anterior = historico['Close'].iloc[-2]
            var = ((atual / anterior) - 1) * 100
            
            st.metric(f"Preço {ticker_final}", f"R$ {atual:.2f}", f"{var:.2f}%")
            
            if abs(var) > 2.0:
                st.warning(f"🚨 MOVIMENTAÇÃO BRUSCA: {ticker_final} variando {var:.2f}%!")
            
            if st.button("✨ Analisar com IA"):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"O ativo {ticker_final} variou {var:.2f}% hoje. Analise isso."}]}]}
                    res = requests.post(url, json=payload, timeout=10)
                    st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                except:
                    st.error("Erro 404: Verifique a chave no Secrets.")
        else:
            st.error("Falha na comunicação com a B3/Mercado.")

    with col2:
        st.subheader(f"📊 Dividendos: {ticker_final}")
        if obj:
            divs = obj.dividends
            if not divs.empty:
                df = divs.tail(15).to_frame().reset_index()
                df.columns = ['Data', 'Valor']
                chart = alt.Chart(df).mark_bar(size=25, color='#008cff').encode(
                    x='Data:T', y='Valor:Q'
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df.sort_values(by='Data', ascending=False), hide_index=True)
            else:
                st.info("Sem histórico de dividendos disponível para este ativo.")
else:
    st.info("👋 Radar Vazio. Escolha um ativo ao lado para o Mentor começar a monitorar.")
