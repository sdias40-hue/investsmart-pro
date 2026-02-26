import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master (Visibilidade Nítida Sandro)
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff !important; }
    h1, h2, h3, h4, p, span, label, div { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; }
    iframe { min-height: 500px !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Inteligência de Carteira
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    # Identifica se é Cripto para mudar os campos de entrada
    is_crypto = "-" in ticker_input or len(ticker_input) > 6
    st.markdown(f"<h4 class='neon-blue'>💰 Gestão: {'Cripto' if is_crypto else 'Ação'}</h4>", unsafe_allow_html=True)
    
    val_investido = st.number_input("Valor total investido (R$):", value=0.0)
    
    if is_crypto:
        preco_pago = st.number_input("Preço de Compra (R$):", value=0.0, format="%.2f")
    else:
        qtd_acoes = st.number_input("Quantidade de Ações:", value=0)
        preco_pago = st.number_input("Preço Médio (R$):", value=0.0, format="%.2f")
    
    if st.sidebar.button("🚀 Sincronizar Tudo"):
        st.rerun()

# 3. Radar Global: Bolsas Mundiais (Novo Avanço)
st.markdown("<h3 class='neon-blue'>🌍 Radar das Bolsas Mundiais</h3>", unsafe_allow_html=True)
indices = {"S&P 500 (EUA)": "^GSPC", "Nasdaq (Tech)": "^IXIC", "Ibovespa (BR)": "^BVSP"}
cols_idx = st.columns(3)

for i, (nome, ticket) in enumerate(indices.items()):
    try:
        idx_data = yf.Ticker(ticket).history(period="2d")
        if len(idx_data) > 1:
            v_at = idx_data['Close'].iloc[-1]
            var = ((v_at / idx_data['Close'].iloc[-2]) - 1) * 100
            cols_idx[i].metric(nome, f"{v_at:,.0f}", f"{var:.2f}%")
    except: pass

# 4. Motor de Busca e Performance
ticker_f = ticker_input + ".SA" if len(ticker_input) < 6 and "." not in ticker_input else ticker_input

try:
    data = yf.download(ticker_f, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # Cálculo de Lucro Inteligente
        if not is_crypto and 'qtd_acoes' in locals() and qtd_acoes > 0:
            lucro_r = (p_atual - preco_pago) * qtd_acoes
        else:
            lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        
        porc = ((p_atual / preco_pago) - 1) * 100 if preco_pago > 0 else 0
        
        c1, c2 = st.columns(2)
        c1.metric("Cotação de Hoje", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {lucro_r:,.2f}", delta=f"{porc:.2f}%")

        # --- ORIENTAÇÃO DO MENTOR (MANTIDA E BLINDADA) ---
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        
        topo_10 = float(data['High'].tail(10).max())
        fundo_10 = float(data['Low'].tail(10).min())
        
        col_compra, col_venda = st.columns(2)
        with col_compra:
            st.markdown(f"<div class='mentor-box'><h4>🛒 Onde Comprar:</h4><p>Preço seguro perto de <b class='neon-blue'>R$ {fundo_10:.2f}</b>.</p></div>", unsafe_allow_html=True)
        with col_venda:
            st.markdown(f"<div class='mentor-box'><h4>💰 Onde Vender:</h4><p>Considere lucrar em <b class='neon-blue'>R$ {topo_10:.2f}</b>.</p></div>", unsafe_allow_html=True)

        # --- GRÁFICO MASTER (RESOLVIDO PARA PC) ---
        st.markdown("<h4 class='neon-blue'>📈 Histórico de Preços</h4>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(7).mean(), name="Tendência", line=dict(color='#00d4ff', width=2)))
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

except Exception: st.error("Sincronizando com os mercados mundiais...")
