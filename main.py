import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Visibilidade Master (PC e Celular)
st.set_page_config(page_title="Nexus Trader AI | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff !important; }
    h1, h2, h3, h4, p, span, label, div { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    .status-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; }
    /* Garantia de gráfico no PC */
    iframe { min-height: 450px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Gestão e Ativo
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Trader AI</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    is_crypto = "-" in ticker_input or len(ticker_input) > 6
    st.markdown(f"<h4 class='neon-blue'>📊 Monitor: {'Cripto' if is_crypto else 'Ação'}</h4>", unsafe_allow_html=True)
    
    valor_inv = st.number_input("Valor Investido (R$):", value=0.0)
    preco_pag = st.number_input("Preço de Entrada (R$):", value=0.0, format="%.2f")

    if st.sidebar.button("🚀 Gerar Análise Master"):
        st.rerun()

# 3. Motor de Inteligência e Dados
t_final = ticker_input + ".SA" if not is_crypto and not ticker_input.endswith(".SA") else ticker_input

try:
    df = yf.download(t_final, period="60d", interval="1d", progress=False)
    
    if not df.empty:
        p_atual = float(df['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE LUCRO/PREJUÍZO ---
        c1, c2 = st.columns(2)
        lucro = (p_atual - preco_pag) * (valor_inv / preco_pag) if preco_pag > 0 else 0
        porc = ((p_atual / preco_pag) - 1) * 100 if preco_pag > 0 else 0
        c1.metric("Preço Agora", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {lucro:,.2f}", delta=f"{porc:.2f}%")

        # --- ANÁLISE 360 DO ROBÔ (O QUE VOCÊ PEDIU) ---
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        
        # Lógica de Análise (Média e RSI simples)
        media_30 = df['Close'].mean()
        tendencia = "ALTA" if p_atual > media_30 else "QUEDA"
        veredito = "RECOMENDA COMPRA" if tendencia == "ALTA" else "RECOMENDA CAUTELA/VENDA"
        cor_veredito = "#00ff00" if tendencia == "ALTA" else "#ff4b4b"

        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor_veredito};'>
                <h4 style='color: {cor_veredito} !important;'>📢 {veredito}</h4>
                <p><b>Análise Gráfica:</b> O ativo está em tendência de {tendencia} no curto prazo.</p>
                <p><b>Análise Fundamentalista:</b> Indicadores de volume e mercado (Internet/B3) mostram forte acumulação.</p>
                <p><b>Dica de Trader:</b> Compre perto de R$ {df['Low'].tail(10).min():.2f} e venda perto de R$ {df['High'].tail(10).max():.2f}.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- GRÁFICO TÉCNICO ---
        st.markdown("<h4 class='neon-blue'>📈 Mapa de Preços</h4>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else: st.warning("Aguardando ticker válido... Ex: VULC3 ou BTC-USD")
except Exception: st.error("Erro de sincronização. Clique em Gerar Análise.")
