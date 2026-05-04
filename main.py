import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests

# --- CONFIGURAÇÕES DO TELEGRAM (Dados extraídos do seu print) ---
TOKEN_TELEGRAM = "COLE_AQUI_O_TOKEN_QUE_O_BOTFATHER_TE_DEU" 
CHAT_ID_TELEGRAM = "8392660003"

def enviar_alerta_telegram(mensagem):
    if "COLE_AQUI" in TOKEN_TELEGRAM:
        return 
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": CHAT_ID_TELEGRAM, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

# 1. Configuração de Visibilidade
st.set_page_config(page_title="Nexus Mentor | Sandro", layout="wide")

st.markdown("""
    <style>
    .stApp, .main, header, .stSidebar, [data-testid="stHeader"] { 
        background-color: #000000 !important; 
    }
    h1, h2, h3, h4, p, span, label, div { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important; 
    }
    .neon-blue { color: #00d4ff !important; font-weight: bold; }

    [data-testid="collapsedControl"] {
        background-color: #00d4ff !important;
        border-radius: 0 12px 12px 0;
        width: 40px !important;
        height: 40px !important;
        top: 15px !important;
        left: 0 !important;
    }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; padding: 10px; }
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Gestão de Ativos
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Mentor</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper().strip()
    
    st.divider()
    st.markdown("<h4 class='neon-blue'>💰 Dados da Carteira</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor total investido (R$):", value=0.0, step=100.0)
    preco_pago = st.number_input("Preço que paguei (Unidade):", value=0.0, format="%.2f")
    
    ativar_alertas = st.checkbox("Ativar Alertas no Telegram", value=True)
    
    if st.sidebar.button("🚀 Sincronizar Tudo"):
        st.rerun()

# 3. Tratamento do Ticker Inteligente
if "-" in ticker_input or "." in ticker_input:
    ticker_f = ticker_input
else:
    ticker_f = ticker_input + ".SA"

# 4. Motor de Busca e Exibição
try:
    data = yf.download(ticker_f, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        variacao = ((p_atual / preco_pago) - 1) * 100 if preco_pago > 0 else 0
        
        c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
        c2.metric("Resultado Estimado", f"R$ {lucro_r:,.2f}", delta=f"{variacao:.2f}%")

        st.divider()
        st.markdown("<h3 class='neon-blue'>💡 Recomendações do Robô</h3>", unsafe_allow_html=True)
        
        topo_10 = float(data['High'].tail(10).max())
        fundo_10 = float(data['Low'].tail(10).min())
        
        col_c, col_v = st.columns(2)
        with col_c:
            st.markdown(f"<div class='mentor-box'><h4>🛒 Suporte (Compra):</h4><p class='neon-blue'>R$ {fundo_10:.2f}</p></div>", unsafe_allow_html=True)
        with col_v:
            st.markdown(f"<div class='mentor-box'><h4>💰 Resistência (Venda):</h4><p class='neon-blue'>R$ {topo_10:.2f}</p></div>", unsafe_allow_html=True)

        # Disparo de Alerta
        if ativar_alertas:
            if p_atual <= fundo_10:
                enviar_alerta_telegram(f"🔔 *OPORTUNIDADE EM SALTO:* {ticker_input} atingiu suporte de R$ {p_atual:.2f}!")
            elif p_atual >= topo_10:
                enviar_alerta_telegram(f"🚀 *ALERTA DE VENDA:* {ticker_input} atingiu topo de R$ {p_atual:.2f}!")

        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='black', plot_bgcolor='black', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(f"Aguardando dados de {ticker_f}...")

except Exception as e:
    st.error(f"Erro: {e}")
