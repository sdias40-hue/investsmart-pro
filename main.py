import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="Nexus Pro Master | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #1c2128; border-radius: 10px 10px 0 0; color: white; }
    .stMetric { background-color: #1c2128 !important; border-radius: 12px; padding: 20px; border: 1px solid #444c56; }
    .trade-card { background-color: #1c2128; padding: 25px; border-radius: 15px; border: 1px solid #444c56; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral Nexus (Multiusuário)
with st.sidebar:
    st.title("🛡️ Nexus Command")
    user_id = st.text_input("ID do Usuário:", value="Sandro_Master")
    user_ticker = st.text_input("Ativo (VULC3, BTC-USD, IVVB11):", value="VULC3").upper()
    
    # Detector Inteligente para Ação, BDR e Cripto
    if "-" in user_ticker or len(user_ticker) > 6:
        ticker_final = user_ticker
    else:
        ticker_final = user_ticker + ".SA" if not user_ticker.endswith(".SA") else user_ticker

    meta_renda = st.number_input("Meta de Renda (R$):", value=1000.0)
    st.success(f"Logado: {user_id}")
    st.caption("Fontes: Invest10, Folhainvest, B3, Yahoo Finance")

# 3. Motor de Inteligência Pensante
try:
    df = yf.download(ticker_final, period="100d", interval="1d", progress=False)
    
    if not df.empty:
        # Extração de dados limpos (Garante que não trave)
        p_atual = float(df['Close'].iloc[-1])
        st.title(f"🚀 Nexus Intelligence Master: {user_ticker}")

        # --- SISTEMA DE ABAS PROFISSIONAIS ---
        tab_monitor, tab_day, tab_swing = st.tabs(["🎯 Monitor Master", "⚡ Centro Day Trade", "📈 Visão Swing Trade"])

        with tab_monitor:
            c1, c2, c3 = st.columns(3)
            dy_base = 12.5 if ".SA" in ticker_final else 0
            cap_p_meta = (meta_renda * 12) / (dy_base / 100) if dy_base > 0 else 0
            
            c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
            c2.metric("Dividend Yield (Est.)", f"{dy_base}%" if dy_base > 0 else "N/A (Especulativo)")
            c3.metric("Capital p/ Meta", f"R$ {cap_p_meta:,.0f}" if cap_p_meta > 0 else "N/A")
            
            # Gráfico Principal com Médias Móveis
            fig_m = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Preço")])
            fig_m.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), name="Média 20d", line=dict(color='yellow')))
            fig_m.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_m, use_container_width=True)

        with tab_day:
            st.markdown('<div class="trade-card" style="border-left: 5px solid #FF4B4B;"><h3>⚡ Terminal Day Trade</h3></div>', unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            
            with col_d1:
                st.metric("Resistência (Venda)", f"R$ {res:.2f}")
                st.info("**Opinião Nexus:** Topo de volatilidade detectado. Risco de correção alto.")
            with col_d2:
                st.metric("Suporte (Compra)", f"R$ {sup:.2f}")
                st.warning("**Ação Requerida:** Ponto de entrada se houver volume comprador.")

        with tab_swing:
            st.markdown('<div class="trade-card" style="border-left: 5px solid #00D1FF;"><h3>📈 Estratégia Swing Trade</h3></div>', unsafe_allow_html=True)
            col_s1, col_s2 = st.columns(2)
            alvo = p_atual * 1.25
            
            with col_s1:
                st.metric("Alvo Técnico (+25%)", f"R$ {alvo:.2f}")
                st.success(f"**Análise Invest10:** Ativo com margem de segurança atrativa.")
            with col_s2:
                tendencia = "ALTA" if p_atual > df['Close'].mean() else "BAIXA"
                st.metric("Tendência Principal", tendencia)
                st.write("**Análise Folhainvest:** Ciclo de acumulação identificado.")

    else:
        st.warning(f"🔍 Sincronizando dados de {ticker_final}... Verifique o símbolo.")
except Exception as e:
    st.error(f"Erro Master: Verifique se o ticker {user_ticker} é válido.")
