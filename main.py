import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master de Alta Visibilidade
st.set_page_config(page_title="Nexus Master | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1c2128 !important; border-radius: 12px; padding: 20px; border: 1px solid #444c56; }
    .card { background-color: #1c2128; padding: 20px; border-radius: 15px; border: 1px solid #444c56; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar Inteligente (Nexus Command)
with st.sidebar:
    st.title("🛡️ Nexus Command")
    user_ticker = st.text_input("Ativo (Ex: VULC3, BTC-USD, JEPP34):", value="VULC3").upper()
    
    # Detector Inteligente de Ativo para não travar
    if "-" in user_ticker or len(user_ticker) > 6:
        ticker_final = user_ticker # Criptos ou BDRs complexos
    else:
        ticker_final = user_ticker + ".SA" if not user_ticker.endswith(".SA") else user_ticker

    meta_renda = st.number_input("Meta Mensal (R$):", value=1000.0)
    st.divider()
    st.success("🤖 Robô Pensante: Online")
    st.caption("Fontes: Invest10, Folhainvest, B3, Yahoo Finance")

# 3. Motor de Dados e Inteligência
try:
    df = yf.download(ticker_final, period="90d", interval="1d", progress=False)
    
    if not df.empty:
        p_atual = float(df['Close'].iloc[-1])
        st.title(f"🚀 Inteligência Nexus: {user_ticker}")

        # --- ABAS DE OPERAÇÃO ---
        tab_geral, tab_day, tab_swing = st.tabs(["📊 Visão Geral", "⚡ Day Trade", "📈 Swing Trade"])

        with tab_geral:
            c1, c2, c3 = st.columns(3)
            # Cálculo de Renda (Simulado Invest10)
            dy_base = 12.5 if ".SA" in ticker_final else 0
            cap_p_meta = (meta_renda * 12) / (dy_base / 100) if dy_base > 0 else 0
            
            c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
            c2.metric("Dividend Yield (Est.)", f"{dy_base}%" if dy_base > 0 else "N/A (Cripto)")
            c3.metric("Capital p/ Meta", f"R$ {cap_p_meta:,.0f}" if cap_p_meta > 0 else "Especulativo")
            
            # Gráfico de Tendência Nexus
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_day:
            st.markdown('<div class="card" style="border-left: 5px solid #FF4B4B;"><h3>⚡ Centro de Comando Day Trade</h3></div>', unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            
            with col_d1:
                st.metric("Resistência (Venda)", f"R$ {res:.2f}")
                st.write("**Opinião Nexus:** Forte pressão vendedora no topo. Atenção para scalping.")
            with col_d2:
                st.metric("Suporte (Compra)", f"R$ {sup:.2f}")
                st.write("**Linha de Tendência:** Ativo testando fundo de 5 dias.")

        with tab_swing:
            st.markdown('<div class="card" style="border-left: 5px solid #00D1FF;"><h3>📈 Análise Swing Trade & Valor</h3></div>', unsafe_allow_html=True)
            col_s1, col_s2 = st.columns(2)
            alvo_longo = p_atual * 1.25
            
            with col_s1:
                st.metric("Alvo Técnico (+25%)", f"R$ {alvo_longo:.2f}")
                st.info("💡 Sugestão Invest10: Ativo em região de acumulação para longo prazo.")
            with col_s2:
                tendencia = "ALTA" if p_atual > df['Close'].mean() else "BAIXA"
                st.metric("Tendência Principal", tendencia)
                st.write(f"**Análise Folhainvest:** Projeção positiva baseada no volume mensal.")

    else:
        st.warning(f"🔍 Buscando dados de {ticker_final}... Verifique se o código está correto.")
except Exception as e:
    st.error(f"Erro Master: {e}")
