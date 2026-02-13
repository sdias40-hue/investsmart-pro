import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import altair as alt

# 1. Layout Premium
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")
st.markdown("<style>.main { background-color: #0e1117; color: white; } [data-testid='column'] { padding: 0 20px !important; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso:", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. RADAR E MONITORAMENTO ---
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_input = st.text_input("Buscar (Ex: BTC-USD, VULC3, BBAS3):", "").upper()
    st.divider()
    st.subheader("💡 Top 5 Fundamentalistas")
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CMIG4"]
    escolha = st.radio("Destaques:", ["Nenhuma"] + sugestoes)
    ticker_final = ticker_input if ticker_input else (escolha if escolha != "Nenhuma" else "")

# --- 4. FUNÇÃO DE DADOS (Diferencial: Redundância de Preço) ---
def buscar_mercado(t):
    try:
        # Tenta rotas variadas para evitar o erro 404
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            # Buscamos um histórico maior para garantir que a variação % seja calculada
            hist = obj.history(period="5d") 
            if not hist.empty:
                return obj, hist
        return None, None
    except:
        return None, None

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Ativos")

if ticker_final:
    obj_ativo, historico = buscar_mercado(ticker_final)
    
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA (Sentinela)")
        if historico is not None:
            # RECUPERANDO O SINAL DE QUEDA/ALTA
            atual = historico['Close'].iloc[-1]
            anterior = historico['Close'].iloc[-2]
            variacao = ((atual / anterior) - 1) * 100
            
            # Exibe o Preço e a Variação logo abaixo (como você pediu)
            st.metric(f"Preço {ticker_final}", f"R$ {atual:.2f}", f"{variacao:.2f}%")
            
            if st.button("✨ Analisar com IA"):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    # Forçando rota v1 estável
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    prompt = f"O ativo {ticker_final} variou {variacao:.2f}% e custa R$ {atual:.2f}. Analise a tendência de dividendos."
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    res = requests.post(url, json=payload, timeout=12)
                    if res.status_code == 200:
                        st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error(f"Erro na IA: {res.status_code}. Verifique a API Key.")
                except:
                    st.error("Falha na comunicação com o Mentor.")
        else:
            st.error("Falha na comunicação: A bolsa não respondeu. Tente CMIG4.")

    with col2:
        st.subheader(f"📊 Histórico: {ticker_final}")
        if obj_ativo:
            divs = obj_ativo.dividends
            if not divs.empty:
                df = divs.tail(15).to_frame().reset_index()
                df.columns = ['Data', 'Valor']
                chart = alt.Chart(df).mark_bar(size=25, color='#008cff').encode(
                    x='Data:T', y='Valor:Q', tooltip=['Data', 'Valor']
                ).properties(height=380)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df.sort_values(by='Data', ascending=False), hide_index=True)
            else:
                st.info("Sem histórico de dividendos para este ticker.")
else:
    st.info("👋 Digite um Ticker ou selecione uma Sugestão ao lado.")
