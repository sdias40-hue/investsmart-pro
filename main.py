import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Setup de Alta Performance
st.set_page_config(page_title="InvestSmart Pro | Final", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso Master:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA CACHEADO ---
@st.cache_data(ttl=900)
def buscar_dados_elite(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="60d")
            if not hist.empty:
                return hist, ticker.info, ticker.dividends.tail(5)
        return None, None, None
    except: return None, None, None

# --- 4. INTERFACE ---
st.title("🏛️ InvestSmart Pro | Terminal de Elite")

with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["VULC3", "BBAS3", "TAEE11", "JEPP34", "SOL-USD"]
    ticker_final = st.text_input("Ticker:", "").upper() or st.selectbox("Favoritos:", [""] + opcoes)

if ticker_final:
    hist, info, divs = buscar_dados_elite(ticker_final)
    if hist is not None:
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        
        col1, col2 = st.columns([1, 2.3])
        
        with col1:
            st.subheader("🤖 Mentor IA Trader")
            st.caption(f"📍 Setor: {info.get('sector', 'Global')}")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço Atual", f"{simbolo} {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            
            # --- SAÚDE FINANCEIRA (A nova sugestão) ---
            st.divider()
            st.write("### 🏥 Saúde Financeira")
            c1, c2 = st.columns(2)
            c1.write(f"**P/L:** {info.get('trailingPE', 'N/A')}")
            c2.write(f"**ROE:** {info.get('returnOnEquity', 0)*100:.1f}%")
            
            # VEREDITO
            if atual > hist['EMA9'].iloc[-1]:
                st.success("✅ GATILHO: Tendência de Alta Confirmada!")
            else:
                st.error("📉 AGUARDE: Tendência de Baixa.")

        with col2:
            st.subheader("📊 Gráfico Candlestick Profissional")
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Velas')])
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='Gatilho', line=dict(color='#ffaa00')))
            fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Resistência")
            fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Suporte")
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # 5. CHATBOT DINÂMICO (Baseado no seu image_f61a59.png)
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Qual sua dúvida sobre este ativo?")
        if pergunta:
            st.write(f"**Mentor responde:** Sobre '{pergunta}', o ativo está em {'alta' if atual > hist.EMA9.iloc[-1] else 'queda'}. Observe o suporte em {simbolo} {sup:,.2f} para sua proteção.")
