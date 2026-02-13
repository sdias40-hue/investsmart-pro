import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Setup de Alta Performance
st.set_page_config(page_title="InvestSmart Pro | Trader", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso Master:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR COM CACHE BLINDADO (Resolvendo image_f5b7a7.png) ---
@st.cache_data(ttl=900)
def buscar_dados_limpos(t):
    try:
        # Tenta rotas para BDRs e Cripto
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="60d")
            if not hist.empty:
                # Guardamos apenas os dados necessários, não o objeto 'ticker' inteiro
                return hist, ticker.info, ticker.dividends.tail(5)
        return None, None, None
    except: return None, None, None

# --- 4. RADAR DE SELEÇÃO ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["VULC3", "BBAS3", "TAEE11", "JEPP34"] if aba == "Ações / BDRs" else ["SOL-USD", "ETH-USD", "BTC-USD"]
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or st.selectbox("Favoritos:", [""] + opcoes)

# --- 5. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Analista de Renda")

if ticker_final:
    hist, info, divs = buscar_dados_limpos(ticker_final)
    
    if hist is not None:
        # Inteligência de Trader (Suporte/Resistência e Médias)
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        ma9 = hist['EMA9'].iloc[-1]
        
        col1, col2 = st.columns([1, 2.3])
        
        with col1:
            st.subheader("🤖 Mentor IA Trader")
            setor = info.get('sector', 'Global / Cripto')
            st.caption(f"📍 Setor: {setor}")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço Atual", f"{simbolo} {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            
            st.divider()
            # CONSELHO DINÂMICO (Como visto no image_f547c6.png)
            if atual > ma9:
                st.success("✅ GATILHO ATIVADO: Tendência de alta confirmada!")
                veredito = "💎 BOA PARA COMPRAR"
            else:
                st.error("📉 AGUARDE: O preço ainda não reagiu.")
                veredito = "⏳ NÃO COMPENSA AGORA"
            
            # ANÁLISE FUNDAMENTALISTA
            if "-" not in ticker_final:
                pago_ano = divs.sum() if not divs.empty else 0
                st.write(f"**Preço Justo (Bazin):** {simbolo} {pago_ano/0.06:,.2f}")
            else:
                st.write("### ⛏️ Renda de Staking")
                st.info("Ativo gera dividendos digitais. Rendimento Est.: 3% a 7% a.a.")

        with col2:
            st.subheader("📊 Gráfico Candlestick Profissional")
            # Gráfico profissional (Resolvendo image_f52ce1.png via Plotly)
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Candles')])
            fig.add_trace(go.Scatter(x=hist.index, y=hist.EMA9, name='Gatilho', line=dict(color='#ffaa00')))
            # Linhas de Trader automáticas
            fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Resistência")
            fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Suporte")
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # 6. CHATBOT MENTOR IA (Como visto no image_f547c6.png)
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Tire suas dúvidas sobre o mercado ou este ativo:")
        if pergunta:
            st.write(f"**Mentor responde:** Sobre '{pergunta}', o ativo está em {'alta' if atual > ma9 else 'queda'}. Observe o suporte em {simbolo} {sup:,.2f} para sua proteção.")

else: st.info("👋 Selecione um ativo para iniciar a análise trader.")
