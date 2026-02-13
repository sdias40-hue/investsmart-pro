import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# 1. Configuração e Estilo
st.set_page_config(page_title="InvestSmart Pro | Trader", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso Master:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR COM CACHE (Blindagem contra RateLimitError) ---
@st.cache_data(ttl=900) # Guarda os dados por 15 minutos
def buscar_dados_seguro(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            h = obj.history(period="60d")
            if not h.empty: return obj, h, obj.info
        return None, None, None
    except Exception as e:
        return None, None, None

# --- 4. RADAR ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["VULC3", "BBAS3", "TAEE11", "JEPP34"] if aba == "Ações / BDRs" else ["SOL-USD", "ETH-USD", "BNB-USD"]
    ticker_final = st.text_input("Digite o Ticker:", "").upper() or st.selectbox("Favoritos:", [""] + opcoes)

# --- 5. INTERFACE ---
if ticker_final:
    obj, hist, info = buscar_dados_seguro(ticker_final)
    if hist is not None:
        # Indicadores de Trader
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        res = hist['High'].max()
        sup = hist['Low'].min()
        atual = hist['Close'].iloc[-1]
        
        col1, col2 = st.columns([1, 2.3])
        with col1:
            st.subheader("🤖 Mentor IA Trader")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}")
            
            # ANÁLISE FUNDAMENTALISTA E RISCO
            st.divider()
            if "-" not in ticker_final: # Ações
                pago_ano = obj.dividends.tail(4).sum()
                st.write(f"**Preço Justo (Bazin):** {simbolo} {pago_ano/0.06:,.2f}")
                st.success("🛡️ PERFIL CONSERVADOR") if pago_ano > 0 else st.error("⚠️ PERFIL AGRESSIVO")
            else: # Criptos (Mentoria Staking)
                st.write("### ⛏️ Mentoria: Staking")
                st.info("Este ativo gera 'Dividendos Digitais'. Rendimento Est.: 3.5% a 7% a.a.")
                st.error("⚠️ PERFIL AGRESSIVO")
            
            # GATILHO TRADER
            if atual > hist['EMA9'].iloc[-1]:
                st.success("✅ GATILHO ATIVADO: Gráfico reagindo para alta!")
            else:
                st.error("📉 AGUARDE: Abaixo da média de gatilho.")

        with col2:
            st.subheader("📊 Gráfico Profissional (Candlestick)")
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Velas')])
            fig.add_trace(go.Scatter(x=hist.index, y=hist.EMA9, name='Gatilho', line=dict(color='#ffaa00', width=2)))
            # Linhas de Trader (Suporte/Resistência)
            fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Resistência")
            fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Suporte")
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450)
            st.plotly_chart(fig, use_container_width=True)
            
        # 6. CHATBOT COM RESPOSTA DINÂMICA
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Qual sua dúvida sobre este ativo?")
        if pergunta:
            st.write(f"**Mentor:** Para responder '{pergunta}', analisei que o ativo está em {'alta' if atual > hist.EMA9.iloc[-1] else 'queda'}. Foque no suporte de {simbolo} {sup:,.2f} como proteção.")

else: st.info("👋 Selecione um ativo para iniciar.")
