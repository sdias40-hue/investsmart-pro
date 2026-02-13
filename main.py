import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração e Estilo
st.set_page_config(page_title="InvestSmart Pro | Terminal Candle", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso ao Terminal:", type="password")
    if st.button("Abrir"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA ---
def buscar_dados(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")] :
            obj = yf.Ticker(s)
            hist = obj.history(period="60d")
            if not hist.empty: return obj, hist, obj.info
        return None, None, None
    except: return None, None, None

# --- 4. INTERFACE ---
st.title("🏛️ InvestSmart Pro | Terminal de Elite")

with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "MXRF11", "JEPP34", "VULC3"] if aba == "Ações / BDRs" else ["BTC-USD", "SOL-USD", "ETH-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or sugestao

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    if hist is not None:
        # Cálculos de Indicadores
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        
        col1, col2 = st.columns([1, 2.5]) # Aumentamos a proporção do gráfico
        
        with col1:
            st.subheader("🤖 Mentor IA")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço Atual", f"{simbolo} {atual:,.2f}")
            
            # --- CÁLCULO DE PREÇO JUSTO ---
            if "-" not in ticker_final:
                pago_ano = obj.dividends.tail(4).sum() if not obj.dividends.empty else 0
                vpa = info.get('bookValue', 0)
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (vpa * 1.5 if vpa > 0 else atual * 0.95)
                st.write(f"### 🎯 Preço Justo: {simbolo} {preco_justo:,.2f}")
            else:
                # Preço justo aproximado para Cripto (Média Móvel)
                ma200 = hist['Close'].mean()
                preco_justo = ma200 * 1.10
                st.write(f"### 🎯 Preço Justo: US$ {preco_justo:,.2f}")
            
            st.divider()
            # GATILHO DE COMPRA
            if atual > hist['EMA9'].iloc[-1]:
                st.success("✅ GATILHO ATIVADO: Tendência de Alta!")
            else:
                st.error("📉 AGUARDE: Tendência de Queda.")

        with col2:
            st.subheader(f"📊 Gráfico Candlestick: {ticker_final}")
            # Criando o gráfico profissional com Plotly
            fig = go.Figure(data=[go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='Candles',
                increasing_line_color= '#00ff00', decreasing_line_color= '#ff0000'
            )])
            
            # Adicionando a Média Móvel (EMA9)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], mode='lines', name='EMA 9', line=dict(color='#ffaa00', width=2)))
            
            fig.update_layout(
                template='plotly_dark',
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)

    # --- ESPAÇO PARA O FUTURO CHATBOT ---
    st.divider()
    st.subheader("💬 Chatbot Mentor IA")
    st.info("Aqui instalaremos o chatbot para responder dúvidas sobre o mercado.")

else:
    st.info("👋 Selecione um ativo para ver o gráfico de Candles.")
