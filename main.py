import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Visibilidade Total (Padronização Sandro Master)
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Fundo Preto e Fontes Brancas para não sumir no PC */
    .main { background-color: #000000; color: #ffffff !important; }
    h1, h2, h3, h4, p, span, label, div { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Cards de Métricas com Borda Azul Neon */
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    
    /* Caixas de Mentor (Onde Comprar/Vender) */
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; }
    
    /* Forçar Gráfico a aparecer no PC */
    iframe { min-height: 500px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Gestão Master
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Dados da Carteira</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor que investi (R$):", value=0.0)
    preco_pago = st.number_input("Preço que paguei:", value=0.0, format="%.2f")
    
    if st.sidebar.button("🚀 Sincronizar Tudo"):
        st.rerun()

# 3. Inteligência de Busca Blindada
ticker_f = ticker_input + ".SA" if len(ticker_input) < 6 and "." not in ticker_input else ticker_input

try:
    # Busca 60 dias para estabilidade no gráfico do PC
    data = yf.download(ticker_f, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE PERFORMANCE ---
        c1, c2 = st.columns(2)
        lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        porc = ((p_atual / preco_pago) - 1) * 100 if preco_pago > 0 else 0
        
        c1.metric("Cotação de Hoje", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {lucro_r:,.2f}", delta=f"{porc:.2f}%")

        # --- ORIENTAÇÃO DO MENTOR (LINGUAGEM FACILITADA) ---
        st.divider()
        st.markdown("<h3 class='neon-blue'>💡 O que o robô recomenda agora?</h3>", unsafe_allow_html=True)
        
        topo_10 = float(data['High'].tail(10).max())
        fundo_10 = float(data['Low'].tail(10).min())
        
        col_compra, col_venda = st.columns(2)
        with col_compra:
            st.markdown(f"<div class='mentor-box'><h4>🛒 Onde Comprar:</h4><p>Preço seguro perto de <b class='neon-blue'>R$ {fundo_10:.2f}</b>.</p></div>", unsafe_allow_html=True)
        
        with col_venda:
            st.markdown(f"<div class='mentor-box'><h4>💰 Onde Vender:</h4><p>Considere vender quando chegar em <b class='neon-blue'>R$ {topo_10:.2f}</b>.</p></div>", unsafe_allow_html=True)

        # --- GRÁFICO MASTER (RESTAURADO PARA PC) ---
        st.markdown("<h4 class='neon-blue'>📈 Histórico de Preços</h4>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        # Linha de tendência Azul Neon
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(7).mean(), name="Tendência", line=dict(color='#00d4ff', width=2)))
        
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else: st.warning("Por favor, digite um código de ativo válido.")
except Exception: st.error("Sincronizando com a Nuvem... Tente atualizar a página.")
