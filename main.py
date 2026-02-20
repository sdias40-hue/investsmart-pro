import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup Visual Premium
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445e; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Alerta
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": mensagem}, timeout=5)
        except: pass

# 3. Base de Conhecimento (Teses de Investimento)
TESES = {
    "OHI": "🏘️ Imóveis de Saúde (EUA). Dono de asilos e hospitais. Renda sólida pelo envelhecimento da população.",
    "JEPP34": "💵 Renda Mensal em Dólar. Fundo focado em gerar dividendos altos todo mês.",
    "BBAS3": "🏦 Banco do Brasil. Líder no Agronegócio. Excelente pagador de dividendos e muito sólido.",
    "TAEE11": "⚡ Transmissão de Energia. Receita garantida por contratos. Considerado um dos mais seguros do Brasil.",
    "BTC-USD": "🪙 Ouro Digital. Reserva de valor limitada para proteção contra a inflação.",
    "SOL-USD": "🚀 Tecnologia. Rede para novos aplicativos digitais. Alto potencial de valorização.",
    "VULC3": "👟 Vulcabras (Olympikus). Setor de consumo. Empresa resiliente com boa margem de lucro."
}

# 4. Motor de Busca
def buscar_dados_v72(t):
    try:
        t_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(t_search)
        hist = ticker.history(period="1d", interval="5m")
        if hist.empty:
            ticker = yf.Ticker(t)
            hist = ticker.history(period="1d", interval="5m")
        return hist, ticker.info, ticker.dividends
    except: return None, None, None

# --- SIDEBAR: CONFIGURAÇÃO DE LICENÇA E ADIÇÃO DE ATIVOS ---
with st.sidebar:
    st.header("🔑 Sua Licença")
    token_cliente = st.text_input("Token do Bot:", type="password")
    id_cliente = st.text_input("Seu Chat ID (Ex: 8392660003):")
    
    st.divider()
    st.header("🎯 Radar de Ativos")
    
    # Busca Manual (O que você pediu!)
    st.subheader("➕ Adicionar Manualmente")
    add_manual = st.text_input("Digite o Ticker (Ex: VALE3, AAPL):").upper()
    
    st.divider()
    # Listas de monitoramento
    mon_cripto = st.multiselect("🪙 Criptos:", ["BTC-USD", "ETH-USD", "SOL-USD"], ["BTC-USD"])
    mon_bdr = st.multiselect("🌎 Internacional:", ["OHI", "JEPP34", "IVVB11"], ["OHI", "JEPP34"])
    mon_acoes = st.multiselect("🇧🇷 Brasil:", ["BBAS3", "TAEE11", "VULC3", "PETR4"], ["BBAS3", "TAEE11"])

    if st.button("🚀 Ligar Terminal"):
        st.session_state.ativo = True
        enviar_alerta_telegram(token_cliente, id_cliente, "🤖 InvestSmart Pro: Monitoramento Iniciado!")

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Central de Renda e Análise")

def exibir_estante(titulo, lista):
    if add_manual and titulo == "🇧🇷 MERCADO BRASILEIRO (AÇÕES)": 
        if add_manual not in lista: lista.append(add_manual)
    
    if lista:
        st.subheader(titulo)
        cols = st.columns(len(lista))
        for i, t in enumerate(lista):
            with cols[i]:
                hist, info, divs = buscar_dados_v72(t)
                if hist is not None and not hist.empty:
                    atual = hist['Close'].iloc[-1]
                    # Dividendos: Mostra o acumulado do último ano
                    dy_total = (divs.tail(12).sum()) if not divs.empty else 0
                    preco_justo = (dy_total / 0.06) if dy_total > 0 else (atual * 1.15)
                    
                    # Layout Preço
                    st.metric(f"💰 {t}", f"R$ {atual:,.2f}", f"{((atual/hist.Open.iloc[0])-1)*100:.2f}%")
                    st.caption(f"🎯 Preço Justo: R$ {preco_justo:,.2f}")
                    
                    # Seção de Dividendos (Nova!)
                    if dy_total > 0:
                        st.write(f"📈 **Renda/Ano:** R$ {dy_total:,.2f}")
                    
                    # Mentor IA
                    tese = TESES.get(t, "Ativo sólido em monitoramento técnico.")
                    st.info(f"**Mentor:** {tese}")
                    
                    # Veredito
                    if atual < preco_justo: st.success("💎 OPORTUNIDADE DE COMPRA")
                    else: st.warning("⏳ AGUARDE UM RECUO")

                    fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#ffaa00', width=2))])
                    fig.update_layout(template='plotly_dark', height=80, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False)
                    st.plotly_chart(fig, use_container_width=True, key=f"s_{t}")
        st.divider()

# Exibição organizada
exibir_estante("🪙 MERCADO CRIPTO", mon_cripto)
exibir_estante("🌎 MERCADO INTERNACIONAL (BDR/ETF)", mon_bdr)
exibir_estante("🇧🇷 MERCADO BRASILEIRO (AÇÕES)", mon_acoes)

# Auto-Refresh
time.sleep(60)
st.rerun()
