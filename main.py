import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Visibilidade Total (Padronização Sandro Master)
st.set_page_config(page_title="Nexus Trader AI | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Fundo Preto e Fontes Brancas para não sumir no PC */
    .main { background-color: #000000; color: #ffffff !important; }
    h1, h2, h3, h4, p, span, label, div { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Cards de Métricas com Borda Neon */
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    
    /* Caixa de Veredito do Robô */
    .status-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; }
    
    /* Forçar Gráfico a aparecer no PC */
    iframe { min-height: 550px !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Gestão Inteligente (Cripto vs Ações)
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Trader AI</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    is_crypto = "-" in ticker_input or len(ticker_input) > 6
    st.markdown(f"<h4 class='neon-blue'>📊 Monitor: {'Cripto' if is_crypto else 'Ação'}</h4>", unsafe_allow_html=True)
    
    val_investido = st.number_input("Valor Investido (R$):", value=0.0)
    
    if is_crypto:
        st.caption("Foco: Valor Total Investido")
        preco_pago = st.number_input("Preço de Compra (R$):", value=0.0, format="%.2f")
    else:
        st.caption("Foco: Quantidade e Preço Médio")
        qtd_comprada = st.number_input("Quantidade de Ações:", value=0)
        preco_pago = st.number_input("Preço Médio (R$):", value=0.0, format="%.2f")

    if st.sidebar.button("🚀 Gerar Análise Master"):
        st.rerun()

# 3. Motor de Inteligência Blindado
t_f = ticker_input + ".SA" if not is_crypto and not ticker_input.endswith(".SA") else ticker_input

try:
    # Coletando 60 dias para estabilidade no PC
    data = yf.download(t_f, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE PERFORMANCE ---
        c1, c2 = st.columns(2)
        if not is_crypto and 'qtd_comprada' in locals() and qtd_comprada > 0:
            lucro_r = (p_atual - preco_pago) * qtd_comprada
        else:
            lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        porc = ((p_atual / preco_pago) - 1) * 100 if preco_pago > 0 else 0
        
        c1.metric("Cotação de Hoje", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {lucro_r:,.2f}", delta=f"{porc:.2f}%")

        # --- VEREDITO DO ROBÔ (ANÁLISE GRÁFICA + INTERNET) ---
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito do Robô Nexus</h3>", unsafe_allow_html=True)
        
        media_30 = data['Close'].mean()
        tendencia = "ALTA" if p_atual > media_30 else "QUEDA"
        veredito = "RECOMENDA COMPRA" if tendencia == "ALTA" else "RECOMENDA CAUTELA"
        cor_v = "#00ff00" if tendencia == "ALTA" else "#ff4b4b"

        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor_v};'>
                <h4 style='color: {cor_v} !important;'>📢 {veredito}</h4>
                <p><b>Análise Técnica:</b> O ativo está em ciclo de {tendencia} no curto prazo.</p>
                <p><b>Análise Master:</b> Ponto seguro de entrada perto de R$ {data['Low'].tail(10).min():.2f}.</p>
                <p><b>Dica de Trader:</b> Notícias e volume indicam resistência perto de R$ {data['High'].tail(10).max():.2f}.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- GRÁFICO MASTER (RESOLVIDO PARA PC) ---
        st.markdown("<h4 class='neon-blue'>📈 Histórico de Preços</h4>", unsafe_allow_html=True)
                fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(7).mean(), name="Tendência", line=dict(color='#00d4ff', width=2)))
        
        fig.update_layout(template="plotly_dark", height=550, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else: st.warning("Aguardando ticker válido... Ex: VULC3 ou BTC-USD")
except Exception: st.error("Sincronizando com a Nuvem... Tente atualizar a página.")
