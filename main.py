import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Setup Profissional
st.set_page_config(page_title="InvestSmart Pro | Terminal Master", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso ao Terminal:", type="password")
    if st.button("Abrir"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA INTELIGENTE ---
def buscar_dados(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="200d")
            if not hist.empty: return obj, hist, obj.info
        return None, None, None
    except: return None, None, None

# --- 4. INTERFACE ---
st.title("🏛️ InvestSmart Pro | Gestor de Renda & Risco")

with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "MXRF11", "JEPP34", "VULC3"] if aba == "Ações / BDRs" else ["BTC-USD", "SOL-USD", "ETH-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or sugestao

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    if hist is not None:
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        hist['MA200'] = hist['Close'].rolling(window=200).mean()
        atual = hist['Close'].iloc[-1]
        
        col1, col2 = st.columns([1, 1.4])
        with col1:
            st.subheader("🤖 Veredito do Mentor")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço Atual", f"{simbolo} {atual:,.2f}")
            
            # --- CÁLCULO DE PREÇO JUSTO ---
            if "-" not in ticker_final:
                pago_ano = obj.dividends.tail(4).sum() if not obj.dividends.empty else 0
                vpa = info.get('bookValue', 0)
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (vpa * 1.5 if vpa > 0 else atual * 0.95)
                st.write(f"### 🎯 Preço Justo: {simbolo} {preco_justo:,.2f}")
            else:
                preco_justo = hist['MA200'].iloc[-1] * 1.15
                st.write(f"### 🎯 Preço Justo (Ciclo): US$ {preco_justo:,.2f}")
            
            # --- MENSAGEM DE AÇÃO ---
            if atual < preco_justo and atual > hist['MA9'].iloc[-1]:
                st.success("✅ BOA PARA COMPRAR: Preço e Gráfico alinhados!")
            elif atual < preco_justo:
                st.info("⏳ AGUARDE: Preço bom, mas o gráfico ainda cai.")
            else:
                st.warning("⚠️ CARO: Preço acima do valor justo.")

        with col2:
            st.subheader("📊 Gráfico de Gatilho")
            chart_data = hist.tail(40).reset_index()
            base = alt.Chart(chart_data).encode(x='Date:T')
            line = base.mark_line(color='#008cff', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
            ma9 = base.mark_line(color='#ffaa00', strokeDash=[5,5]).encode(y='MA9:Q')
            st.altair_chart(line + ma9, use_container_width=True)

    # --- RESERVA PARA O CHATBOT ---
    st.divider()
    st.subheader("💬 Chatbot Mentor IA")
    pergunta = st.text_input("Como posso ajudar na sua decisão hoje?", placeholder="Digite sua dúvida aqui (em breve disponível)...", disabled=True)
else:
    st.info("👋 Radar pronto. Escolha um ativo para começar.")
