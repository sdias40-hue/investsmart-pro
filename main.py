import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests

# --- CONFIGURAÇÕES DO TELEGRAM ---
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI" 
CHAT_ID_TELEGRAM = "8392660003"

def enviar_alerta_telegram(mensagem):
    if "SEU_TOKEN" in TOKEN_TELEGRAM:
        return 
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID_TELEGRAM, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

# 1. Configuração de Visibilidade
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    .stApp, .main, header, .stSidebar, [data-testid="stHeader"] { background-color: #000000 !important; }
    h1, h2, h3, h4, p, span, label, div { color: #ffffff !important; font-family: 'Segoe UI', sans-serif !important; }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    
    # LIMPEZA TOTAL: Remove espaços, pontos e textos extras como "S.A"
    raw_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    ticker_clean = raw_input.replace(" ", "").replace("S.A", "").replace("SA", "").strip()
    
    st.divider()
    val_investido = st.number_input("Valor total investido (R$):", value=0.0)
    preco_pago = st.number_input("Preço que paguei (Unidade):", value=0.0)
    ativar_alertas = st.checkbox("Ativar Alertas no Telegram", value=True)
    
    if st.sidebar.button("🚀 Sincronizar Tudo"):
        st.rerun()

# 3. Formatação do Ticker (Lógica B3 vs Internacional)
ticker_f = ticker_clean if "-" in ticker_clean or "." in ticker_clean else f"{ticker_clean}.SA"

# 4. Busca de Dados
try:
    # Adicionamos auto_adjust para evitar erros de formatação
    data = yf.download(ticker_f, period="60d", interval="1d", progress=False, auto_adjust=True)
    
    # Corrige o problema de colunas duplas que vimos na imagem anterior
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if not data.empty and len(data) > 0:
        p_atual = float(data['Close'].iloc[-1])
        
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_clean}</span></h1>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        variacao = ((p_atual / preco_pago) - 1) * 100 if preco_pago > 0 else 0
        
        c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
        c2.metric("Resultado", f"R$ {lucro_r:,.2f}", delta=f"{variacao:.2f}%")

        # Cálculo de Suporte e Resistência (10 dias)
        topo_10 = float(data['High'].tail(10).max())
        fundo_10 = float(data['Low'].tail(10).min())
        
        st.divider()
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='mentor-box'><h4>🛒 Suporte (10d):</h4><p class='neon-blue'>R$ {fundo_10:.2f}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='mentor-box'><h4>💰 Resistência (10d):</h4><p class='neon-blue'>R$ {topo_10:.2f}</p></div>", unsafe_allow_html=True)

        if ativar_alertas:
            if p_atual <= fundo_10:
                enviar_alerta_telegram(f"🔔 *COMPRA:* {ticker_clean} em R$ {p_atual:.2f}")
            elif p_atual >= topo_10:
                enviar_alerta_telegram(f"🚀 *VENDA:* {ticker_clean} em R$ {p_atual:.2f}")

        # Gráfico Master
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.update_layout(template="plotly_dark", height=400, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"O Yahoo Finance bloqueou a requisição ou o ativo '{ticker_f}' é inválido. Aguarde 2 minutos.")

except Exception as e:
    st.error(f"Erro inesperado: {e}")
