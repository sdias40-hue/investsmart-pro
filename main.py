import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import altair as alt

# 1. Configuração e Estilo Premium
st.set_page_config(page_title="InvestSmart Pro", layout="wide", page_icon="📈")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    [data-testid="column"] { padding: 0 25px !important; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso:", type="password")
    if st.button("Acessar Terminal"):
        if senha == "sandro2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- 3. RADAR E SUGESTÕES (Ticker Inicial Vazio) ---
with st.sidebar:
    st.header("🔍 Radar de Ativos")
    ticker_manual = st.text_input("Digite o Ticker (Ex: BTC-USD, PETR4):", "").upper()
    
    st.divider()
    st.subheader("💡 Top 5 Fundamentalistas")
    sugestoes = ["JEPP34", "BBAS3", "TAEE11", "PETR4", "CMIG4"]
    escolha = st.radio("Destaques:", ["Nenhuma"] + sugestoes)
    
    ticker_final = ticker_manual if ticker_manual else (escolha if escolha != "Nenhuma" else "")

# --- 4. MOTOR DE COMUNICAÇÃO (Sentinela) ---
@st.cache_data(ttl=60) # Atualiza a cada 1 minuto para o Mentor ficar alerta
def monitorar_mercado(t):
    try:
        simbolos = [f"{t}.SA", t, t.replace(".SA", "")]
        for s in simbolos:
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
    obj_ativo, historico = monitorar_mercado(ticker_final)
    
    col1, col2 = st.columns([1, 1.4], gap="large")

    with col1:
        st.subheader("🤖 Mentor IA (Alerta Ativo)")
        if historico is not None:
            # Lógica de Alerta de Movimentação
            preco_atual = historico['Close'].iloc[-1]
            preco_ant = historico['Close'].iloc[-2]
            variacao = ((preco_atual / preco_ant) - 1) * 100
            
            st.metric("Preço Atual", f"R$ {preco_atual:.2f}", f"{variacao:.2f}%")
            
            if abs(variacao) > 1.5:
                st.warning(f"⚠️ Alerta: {ticker_final} com forte movimentação de {variacao:.2f}%!")
            
            if st.button("✨ Analisar Tendência"):
                try:
                    key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
                    payload = {"contents": [{"parts": [{"text": f"O ativo {ticker_final} variou {variacao:.2f}% hoje. Analise o impacto disso nos dividendos."}]}]}
                    res = requests.post(url, json=payload, timeout=10)
                    st.info(res.json()['candidates'][0]['content']['parts'][0]['text'])
                except:
                    st.error("Erro na IA: 404. Verifique a chave no Secrets.")
        else:
            st.error("Erro de comunicação com a B3. Tente outro ticker.")

    with col2:
        st.subheader(f"📊 Dividendos: {ticker_final}")
        if obj_ativo:
            divs = obj_ativo.dividends
            if not divs.empty:
                df = divs.tail(15).to_frame().reset_index()
                df.columns = ['Data', 'Valor']
                chart = alt.Chart(df).mark_bar(size=28, color='#008cff').encode(
                    x='Data:T', y='Valor:Q', tooltip=['Data', alt.Tooltip('Valor', format='.3f')]
                ).properties(height=380)
                st.altair_chart(chart, use_container_width=True)
                st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("Ativo sem histórico de dividendos disponível.")
else:
    st.info("👋 Radar Vazio. Digite um ativo ou selecione uma sugestão para monitorar.")
