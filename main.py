import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. Configuração e Estilo Profissional
st.set_page_config(page_title="InvestSmart Pro | Terminal Candle", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso ao Terminal:", type="password")
    if st.button("Abrir"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA (Blindado para BDRs e Erros 404) ---
def buscar_dados(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="60d")
            if not hist.empty: return obj, hist, obj.info
        return None, None, None
    except: return None, None, None

# --- 4. RADAR DE SELEÇÃO ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "JEPP34", "MXRF11"] if aba == "Ações / BDRs" else ["SOL-USD", "ETH-USD", "BTC-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or sugestao

# --- 5. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Analista de Renda")

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    if hist is not None:
        # Cálculos Técnicos (Média Móvel EMA9)
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['EMA9'].iloc[-1]
        var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        
        col1, col2 = st.columns([1, 2.5])
        
        with col1:
            st.subheader("🤖 Mentor InvestSmart")
            # Setor e Perfil (Como visto no image_d9f29a.jpg)
            setor = info.get('sector', 'Global / Cripto')
            st.caption(f"📍 Setor: {setor}")
            
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço Atual", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            st.divider()
            st.write("### 📜 Conselho & Gatilho")
            
            # GATILHO DE COMPRA (O que você pediu para avisar)
            if atual > ma9_atual:
                st.success("✅ GATILHO ATIVADO: O gráfico reagiu! Tendência de alta confirmada.")
            else:
                st.error("📉 AGUARDE: O preço ainda está abaixo da média de segurança.")

            # PREÇO JUSTO & RENDA
            if "-" not in ticker_final:
                pago_ano = obj.dividends.tail(4).sum() if not obj.dividends.empty else 0
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (info.get('bookValue', 0) * 1.5)
                st.write(f"**Preço Justo:** {simbolo} {preco_justo:,.2f}")
                if atual < preco_justo: st.success("💎 Ativo abaixo do preço justo!")
            else:
                # Informação de Staking (Renda Cripto)
                st.write("### ⛏️ Renda de Staking")
                st.info("Ativo elegível para Staking (Dividendos Cripto). Estimativa: 3.5% a 7% a.a.")

        with col2:
            st.subheader(f"📊 Gráfico Profissional: {ticker_final}")
            # Gráfico de Candlestick (Igual da Bolsa)
            fig = go.Figure(data=[go.Candlestick(
                x=hist.index, open=hist['Open'], high=hist['High'],
                low=hist['Low'], close=hist['Close'], name='Velas'
            )])
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], mode='lines', name='Média Gatilho', line=dict(color='#ffaa00')))
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # ESPAÇO DO CHATBOT (Preparado)
    st.divider()
    st.subheader("💬 Chatbot Mentor (Fase de Mentoria)")
    st.text_input("Pergunte algo sobre Staking ou Dividendos:", disabled=True, placeholder="Em breve...")

else:
    st.info("👋 Selecione um ativo para ver a análise massiva de Candles.")
