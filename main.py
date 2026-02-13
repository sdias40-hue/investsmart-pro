import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import altair as alt

# 1. Configuração e Estilo Premium
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")
st.markdown("<style>.main { background-color: #0e1117; color: white; } [data-testid='column'] { padding: 0 25px !important; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso:", type="password")
    if st.button("Entrar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. RADAR SENTINELA ---
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_input = st.text_input("Buscar (Ex: BTC-USD, VULC3, JEPP34):", "").upper()
    
    st.divider()
    st.subheader("💡 Top 5 Fundamentalistas")
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CMIG4"]
    escolha = st.radio("Destaques:", ["Nenhuma"] + sugestoes)
    
    ticker_final = ticker_input if ticker_input else (escolha if escolha != "Nenhuma" else "")

# --- 4. FUNÇÃO DE DADOS (Sem Cache para evitar Erro de Serialização) ---
def obter_dados_frescos(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="2d")
            if not hist.empty:
                return obj, hist
        return None, None
    except:
        return None, None

# --- INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Ativos")

if ticker_final:
    obj_ativo, historico = obter_dados_frescos(ticker_final)
    
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA (Alerta)")
        if historico is not None:
            # Monitoramento Visual (Já funcional no v28)
            atual = historico['Close'].iloc[-1]
            var = ((atual / historico['Close'].iloc[-2]) - 1) * 100
            st.metric(f"Preço {ticker_final}", f"R$ {atual:.2f}", f"{var:.2f}%")
            
            if st.button("✨ Analisar Tendência"):
                try:
                    # ROTA MESTRA: v1beta com payload simplificado para evitar Erro 404
                    key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                    prompt = f"O ativo {ticker_final} está em R$ {atual:.2f} com variação de {var:.2f}%. Dê um insight curto sobre dividendos."
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    
                    res = requests.post(url, json=payload, timeout=10)
                    if res.status_code == 200:
                        st.success("Análise do Mentor:")
                        st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                    else:
                        st.error(f"Erro {res.status_code}: Tente trocar 'v1beta' para 'v1' no código se o erro persistir.")
                except:
                    st.error("Falha técnica no cérebro da IA.")
        else:
            st.error("Falha na comunicação com o Mercado.")

    with col2:
        st.subheader(f"📊 Histórico: {ticker_final}")
        if obj_ativo:
            divs = obj_ativo.dividends
            if not divs.empty:
                df = divs.tail(15).to_frame().reset_index()
                df.columns = ['Data', 'Valor']
                # Gráfico de Barras Separadas Profissional
                chart = alt.Chart(df).mark_bar(size=30, color='#008cff').encode(
                    x=alt.X('Data:T', title='Data'),
                    y=alt.Y('Valor:Q', title='R$'),
                    tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=380)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df.sort_values(by='Data', ascending=False), hide_index=True)
            else:
                st.info("Ativo sem histórico de proventos.")
else:
    st.info("👋 Digite um Ticker ou selecione uma Sugestão ao lado.")
