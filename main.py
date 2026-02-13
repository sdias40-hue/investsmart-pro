import streamlit as st
import yfinance as yf
import pandas as pd

# Tenta importar o Plotly; se falhar, o robô avisa o que fazer
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Terminal Candle", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso ao Terminal:", type="password")
    if st.button("Abrir"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA (Blindado) ---
def buscar_dados(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="60d")
            if not hist.empty: return obj, hist, obj.info
        return None, None, None
    except: return None, None, None

# --- 4. RADAR MASTER ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "JEPP34", "MXRF11"] if aba == "Ações / BDRs" else ["SOL-USD", "ETH-USD", "BTC-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or sugestao

# --- 5. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Elite")

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    if hist is not None:
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['EMA9'].iloc[-1]
        var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        
        col1, col2 = st.columns([1, 2.5])
        
        with col1:
            st.subheader("🤖 Mentor InvestSmart")
            st.caption(f"📍 Setor: {info.get('sector', 'Global / Cripto')}")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço Atual", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            st.divider()
            st.write("### 📜 Conselho & Gatilho")
            
            if atual > ma9_atual:
                st.success("✅ GATILHO ATIVADO: Tendência de alta confirmada!")
            else:
                st.error("📉 AGUARDE: O preço ainda está abaixo da média de segurança.")

            # PREÇO JUSTO
            pago_ano = obj.dividends.tail(4).sum() if not obj.dividends.empty else 0
            preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (info.get('bookValue', 0) * 1.5)
            st.write(f"**Preço Justo:** {simbolo} {preco_justo:,.2f}")
            if atual < preco_justo: st.success("💎 Ativo abaixo do preço justo!")

        with col2:
            st.subheader(f"📊 Gráfico Profissional: {ticker_final}")
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'], name='Velas'
                )])
                fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], mode='lines', name='EMA 9', line=dict(color='#ffaa00')))
                fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Instale 'plotly' no seu projeto para ver o gráfico de Candles.")
                st.line_chart(hist['Close'])

    st.divider()
    st.subheader("💬 Chatbot Mentor IA")
    st.info("Espaço reservado para a mentoria de Staking e Dividendos.")
else:
    st.info("👋 Selecione um ativo para iniciar a análise massiva.")
