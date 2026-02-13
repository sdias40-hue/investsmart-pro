import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Setup de Alta Performance
st.set_page_config(page_title="InvestSmart Pro | Terminal Master", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso Master:", type="password")
    if st.button("Abrir Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA COM CACHE ---
@st.cache_data(ttl=900)
def buscar_dados_master(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="60d")
            if not hist.empty:
                return hist, ticker.info, ticker.dividends.tail(5)
        return None, None, None
    except: return None, None, None

# --- 4. RADAR DE SELEÇÃO (Top 5 Ações e Criptos) ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    
    if aba == "Ações / BDRs":
        # Top 5 Ações sugeridas para dividendos/valor
        opcoes = ["BBAS3", "TAEE11", "VULC3", "PETR4", "VALE3"]
    else:
        # Top 5 Criptos sugeridas para Staking/Crescimento
        opcoes = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOT-USD"]
        
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or st.selectbox("Top 5 Recomendadas:", [""] + opcoes)

# --- 5. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestor de Renda")

if ticker_final:
    hist, info, divs = buscar_dados_master(ticker_final)
    if hist is not None:
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        ma9 = hist['EMA9'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        
        col1, col2 = st.columns([1, 2.3])
        
        with col1:
            st.subheader("🤖 Veredito do Mentor")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            
            # --- CÁLCULO DE PREÇO JUSTO ---
            st.divider()
            if "-" not in ticker_final:
                pago_ano = divs.sum() if not divs.empty else 0
                # Modelo de Bazin (Dividendos / 0.06)
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (info.get('bookValue', 0) * 1.5)
                st.write(f"### 🎯 Preço Justo: {simbolo} {preco_justo:,.2f}")
                if atual < preco_justo:
                    st.success("💎 ATIVO BARATO (Abaixo do Valor Justo)")
                else:
                    st.warning("⚠️ ATIVO CARO (Acima do Valor Justo)")
            else:
                # Preço Justo Cripto baseado na Média de 60 dias (Suporte)
                st.write(f"### 🎯 Suporte de Preço: {simbolo} {sup:,.2f}")
                st.info("Ativo de Tecnologia: Foco em Staking e Acúmulo.")

            # SAÚDE FINANCEIRA
            st.write("---")
            st.write("📊 **Saúde Financeira:**")
            c1, c2 = st.columns(2)
            c1.write(f"**P/L:** {info.get('trailingPE', 'N/A')}")
            c2.write(f"**ROE:** {info.get('returnOnEquity', 0)*100:.1f}%")

            # GATILHO DE COMPRA
            if atual > ma9:
                st.success("✅ GATILHO: Tendência de Alta!")
            else:
                st.error("📉 AGUARDE: Tendência de Baixa.")

        with col2:
            st.subheader("📊 Gráfico Trader (Candlestick)")
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Velas')])
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='Média Gatilho', line=dict(color='#ffaa00')))
            fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Resistência")
            fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Suporte")
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # 6. CHATBOT MENTOR
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Dúvida sobre este ativo ou mercado?")
        if pergunta:
            st.write(f"**Mentor:** Analisando '{pergunta}'... O ativo está em {'alta' if atual > ma9 else 'queda'}. Com um suporte em {simbolo} {sup:,.2f}, sua margem de segurança está bem definida.")

else: st.info("👋 Escolha uma das Top 5 no Radar ou digite um ticker.")
