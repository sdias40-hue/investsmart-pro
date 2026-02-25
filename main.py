import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. VISIBILIDADE MASTER (PC E CELULAR)
st.set_page_config(page_title="Nexus Global Trader | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    /* Forçar Branco Puro em todas as telas */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .status-box { background-color: #0e1117; border: 1px solid #00d4ff; border-left: 10px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    /* Proteção para o gráfico aparecer no computador */
    .stPlotlyChart { min-height: 550px !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. COMANDO LATERAL (GESTÃO INTELIGENTE)
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Global</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD, VULC3, AAPL):", value="BTC-USD").upper()
    
    st.divider()
    is_crypto = "-" in ticker_input or len(ticker_input) > 6
    st.markdown(f"<p class='neon-blue'>Gestão: {'Cripto' if is_crypto else 'Ações'}</p>", unsafe_allow_html=True)
    
    val_investido = st.number_input("Quanto investi (R$):", value=0.0)
    
    if is_crypto:
        preco_pago = st.number_input("Preço que paguei (R$):", value=0.0, format="%.2f")
    else:
        qtd_comprada = st.number_input("Quantidade de Ações:", value=0)
        preco_pago = st.number_input("Preço Médio (R$):", value=0.0, format="%.2f")

    if st.sidebar.button("🚀 Gerar Inteligência Master"):
        st.rerun()

# 3. RADAR DAS BOLSAS MUNDIAIS (INFLUÊNCIA GLOBAL)
st.markdown("<h3 class='neon-blue'>🌍 Radar das Bolsas Mundiais</h3>", unsafe_allow_html=True)
indices = {"S&P 500 (EUA)": "^GSPC", "Nasdaq (Tech EUA)": "^IXIC", "Ibovespa (Brasil)": "^BVSP"}
cols = st.columns(len(indices))

for i, (nome, ticket) in enumerate(indices.items()):
    try:
        idx_data = yf.Ticker(ticket).history(period="2d")
        if len(idx_data) > 1:
            v_atual = idx_data['Close'].iloc[-1]
            var = ((v_atual / idx_data['Close'].iloc[-2]) - 1) * 100
            cols[i].metric(nome, f"{v_atual:,.0f}", f"{var:.2f}%")
    except: pass

# 4. MOTOR DE INTELIGÊNCIA DO ATIVO
t_final = ticker_input + ".SA" if not is_crypto and "." not in ticker_input and len(ticker_input) < 6 else ticker_input

try:
    # yf.download é mais estável para evitar erros de sincronização
    data = yf.download(t_final, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # PERFORMANCE REAL
        c1, c2 = st.columns(2)
        if not is_crypto and 'qtd_comprada' in locals() and qtd_comprada > 0:
            lucro_r = (p_atual - preco_pago) * qtd_comprada
        else:
            lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        
        c1.metric("Preço Agora", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {lucro_r:,.2f}", delta=f"{((p_atual/preco_pago)-1)*100:.2f}%" if preco_pago > 0 else "0%")

        # VEREDITO E ANÁLISE DO ROBÔ
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        tendencia = "ALTA" if p_atual > data['Close'].mean() else "QUEDA"
        cor_v = "#00ff00" if tendencia == "ALTA" else "#ff4b4b"

        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor_v};'>
                <h4 style='color: {cor_v} !important;'>📢 RECOMENDAÇÃO: {tendencia}</h4>
                <p><b>Análise Master:</b> O ativo está em ciclo de {tendencia}. Suporte forte em R$ {data['Low'].tail(10).min():.2f}.</p>
                <p><b>Influência Global:</b> Acompanhe os EUA acima; se o S&P 500 subir, o ativo tende a ganhar força.</p>
                <p><b>Dica do Mentor:</b> Considere realizar lucros se chegar perto de R$ {data['High'].tail(10).max():.2f}.</p>
            </div>
        """, unsafe_allow_html=True)

        # GRÁFICO (RESTAURADO E FORÇADO PARA PC)
        st.markdown("<h4 class='neon-blue'>📈 Mapa de Preços</h4>", unsafe_allow_html=True)
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else: st.warning("Digite um código válido... Ex: VULC3 ou BTC-USD")
except Exception: st.error("Sincronizando com a Nuvem... Clique em 'Gerar Inteligência Master'.")
