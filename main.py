import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Configuração de Interface Enterprise
st.set_page_config(page_title="InvestSmart Pro | Multi-Monitor", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Motor de Alerta Telegram
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {"chat_id": chat_id, "text": mensagem}
            requests.post(url, data=data)
        except: pass

# 3. Dicionário de Teses (Para Leigos)
TESES = {
    "OHI": "Setor de Saúde (EUA). Investe em asilos e hospitais. Produto sólido pela demanda demográfica (envelhecimento).",
    "JEPP34": "Renda Passiva Dolarizada. Usa estratégia de opções para pagar dividendos mensais altos. Ideal para quem busca fluxo de caixa.",
    "BBAS3": "Setor Bancário (Brasil). Banco sólido com forte participação no Agronegócio. Historicamente bom pagador de dividendos.",
    "BTC-USD": "Ouro Digital. Ativo escasso, usado como proteção contra a inflação das moedas tradicionais.",
    "SOL-USD": "Infraestrutura de Tecnologia. Rede rápida para aplicativos e finanças digitais. Alta volatilidade (risco maior).",
    "TAEE11": "Setor de Energia. Empresa de transmissão. Receita previsível e contratos longos. Muito segura para iniciantes."
}

# 4. Motor de Busca de Dados
def buscar_dados(t):
    try:
        t_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(t_search)
        hist = ticker.history(period="1d", interval="5m") # 5m para dar conta de múltiplos ativos
        return hist, ticker.info
    except: return None, None

# --- SIDEBAR: CONFIGURAÇÃO DE MONITORAMENTO ---
with st.sidebar:
    st.header("🔑 Configuração do Bot")
    token_cliente = st.text_input("Token do Bot:", type="password")
    id_cliente = st.text_input("Seu Chat ID:")
    
    st.divider()
    st.header("🔍 Radar Multi-Ativos")
    st.info("Escolha os ativos para monitoramento simultâneo.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        m_acoes = st.multiselect("Ações (B3):", ["BBAS3", "PETR4", "VALE3", "TAEE11", "VULC3"], ["BBAS3", "TAEE11"])
        m_bdr = st.multiselect("BDR/ETFs:", ["OHI", "JEPP34", "A1IV34", "IVVB11"], ["OHI", "JEPP34"])
    with col_b:
        m_cripto = st.multiselect("Criptos:", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"], ["BTC-USD", "SOL-USD"])

    st.divider()
    if st.button("🚀 Iniciar Monitoramento"):
        st.session_state.monitorando = True
        enviar_alerta_telegram(token_cliente, id_cliente, "🕵️‍♂️ Monitoramento Multi-Ativos Iniciado!")

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Painel de Monitoramento Estratégico")

ativos_para_monitorar = m_acoes + m_bdr + m_cripto

if ativos_para_monitorar:
    cols = st.columns(3) # Grade de 3 colunas para os ativos
    
    for i, t in enumerate(ativos_para_monitorar):
        with cols[i % 3]:
            hist, info = buscar_dados(t)
            if hist is not None and not hist.empty:
                atual = hist['Close'].iloc[-1]
                abertura = hist['Open'].iloc[0]
                var = ((atual/abertura)-1)*100
                
                # Card do Ativo
                with st.container():
                    st.markdown(f"### {t}")
                    st.metric("Preço", f"{atual:,.2f}", f"{var:.2f}%")
                    
                    # Mentor IA - Análise para Leigos
                    tese = TESES.get(t, "Ativo de mercado global com análise técnica baseada em volume.")
                    
                    st.markdown(f"**O que é?** {tese}")
                    
                    # Veredito Estratégico
                    if var > 1.5:
                        st.success("🔥 MOMENTO: Compra Forte (Tendência de Alta)")
                        if i == 0: # Alerta para o primeiro ativo apenas para não spammar
                             enviar_alerta_telegram(token_cliente, id_cliente, f"🚀 SINAL: {t} subindo forte ({var:.2f}%)")
                    elif var < -1.5:
                        st.error("⚠️ CUIDADO: Queda acentuada. Aguarde suporte.")
                    else:
                        st.warning("⚖️ NEUTRO: Momento de observação.")
                    
                    # Gráfico Miniatura (Sparkline)
                    fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#ffaa00', width=2))])
                    fig.update_layout(template='plotly_dark', height=100, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False)
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{t}")
            st.divider()

    time.sleep(60)
    st.rerun()
