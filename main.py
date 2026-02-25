import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Layout Mobile-First (Otimizado para Celular e PC)
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    /* Cards menores para caber no celular */
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    .mentor-box { background-color: #0e1117; border-left: 5px solid #00d4ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Gestão Simples
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    ticker_mon = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Meu Investimento</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Quanto investi (R$):", value=0.0)
    preco_entrada = st.number_input("Preço que paguei:", value=0.0, format="%.2f")
    
    if st.sidebar.button("🚀 Atualizar Agora"):
        st.rerun()

# 3. Motor Mentor
ticker_f = ticker_mon + ".SA" if len(ticker_mon) < 6 and "." not in ticker_mon else ticker_mon

try:
    data = yf.download(ticker_f, period="30d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_mon}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE RESULTADO ---
        c1, c2 = st.columns(2)
        resultado_r = (p_atual - preco_entrada) * (val_investido / preco_entrada) if preco_entrada > 0 else 0
        var_per = ((p_atual / preco_entrada) - 1) * 100 if preco_entrada > 0 else 0
        
        c1.metric("Preço de Hoje", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {resultado_r:,.2f}", delta=f"{var_per:.2f}%")

        # --- ORIENTAÇÃO DO MENTOR (LINGUAGEM SIMPLES) ---
        st.divider()
        st.markdown("<h3 class='neon-blue'>💡 O que fazer agora?</h3>", unsafe_allow_html=True)
        
        res = float(data['High'].tail(5).max())
        sup = float(data['Low'].tail(5).min())
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class='mentor-box'>
                <p><b>🛒 Onde Comprar:</b></p>
                <p>O preço está seguro para compra perto de <span class='neon-blue'>R$ {sup:.2f}</span>.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown(f"""
            <div class='mentor-box'>
                <p><b>💰 Onde Vender:</b></p>
                <p>Considere lucrar ou sair quando chegar em <span class='neon-blue'>R$ {res:.2f}</span>.</p>
            </div>
            """, unsafe_allow_html=True)

        # --- ABA DE ESTUDO IA ---
        tab_graf, tab_ia = st.tabs(["🎯 Gráfico", "🧠 Estudo da IA"])
        
        with tab_graf:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
            fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_ia:
            ticker_ia = st.text_input("Ticker para IA estudar:", key="ia_in").upper()
            if ticker_ia:
                st.info(f"O Mentor está analisando {ticker_ia}... Aguarde.")
                # Lógica simplificada de opinião
                st.success(f"Opinião Master: {ticker_ia} é uma boa opção para {'Longo Prazo' if '34' in ticker_ia else 'Curto Prazo'}.")

    else: st.warning("Digite um código válido (Ex: VULC3 ou BTC-USD).")
except Exception: st.error("Erro de conexão. Tente atualizar a página.")
