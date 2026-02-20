import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface Limpa
st.set_page_config(page_title="InvestSmart Pro | Prateleira", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Motor de Alerta
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": mensagem})
        except: pass

# 3. Dicionário de Teses (Base de Conhecimento para o Cliente)
TESES = {
    "OHI": "🏘️ Imóveis de Saúde (EUA). Dono de asilos e hospitais. Renda sólida pelo envelhecimento da população.",
    "JEPP34": "💵 Renda Mensal em Dólar. Fundo que usa inteligência para pagar dividendos todo mês.",
    "BBAS3": "🏦 Banco do Brasil. Líder no Agronegócio. Empresa estatal sólida e excelente pagadora de dividendos.",
    "TAEE11": "⚡ Energia (Transmissão). Receita garantida por contratos longos. É o investimento mais seguro da B3.",
    "BTC-USD": "🪙 Ouro Digital. Reserva de valor limitada. Proteção contra a perda de valor do dinheiro real.",
    "SOL-USD": "🚀 Tecnologia Rápida. Plataforma para novos aplicativos digitais. Alto potencial de crescimento."
}

# 4. Motor de Busca de Dados
def buscar_dados_simples(t):
    try:
        t_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(t_search)
        hist = ticker.history(period="1d", interval="5m")
        return hist, ticker.info
    except: return None, None

# --- SIDEBAR: CONFIGURAÇÃO SIMPLIFICADA ---
with st.sidebar:
    st.header("🔑 Sua Licença")
    token_cliente = st.text_input("Token do Bot:", type="password", help="Insira o token do seu Telegram")
    id_cliente = st.text_input("Seu ID:", help="Insira seu Chat ID")
    
    st.divider()
    st.header("🎯 Escolha o que Monitorar")
    
    # Seleção por Categoria (Simplificado para o usuário)
    monitor_cripto = st.multiselect("🪙 Criptos:", ["BTC-USD", "ETH-USD", "SOL-USD"], ["BTC-USD"])
    monitor_bdr = st.multiselect("🌎 BDR / ETF (EUA):", ["OHI", "JEPP34", "IVVB11"], ["OHI", "JEPP34"])
    monitor_acoes = st.multiselect("🇧🇷 Ações (Brasil):", ["BBAS3", "TAEE11", "PETR4", "VULC3"], ["BBAS3", "TAEE11"])

    if st.button("🚀 Ligar Terminal"):
        st.session_state.ativo = True
        enviar_alerta_telegram(token_cliente, id_cliente, "🤖 InvestSmart Online: Monitorando sua carteira!")

# --- PAINEL PRINCIPAL (O QUE VOCÊ PEDIU) ---
st.title("🏛️ InvestSmart Pro | Sua Central de Renda")

def exibir_categoria(titulo, lista_ativos):
    if lista_ativos:
        st.subheader(titulo)
        cols = st.columns(len(lista_ativos))
        for i, t in enumerate(lista_ativos):
            with cols[i]:
                hist, info = buscar_dados_simples(t)
                if hist is not None and not hist.empty:
                    atual = hist['Close'].iloc[-1]
                    # Cálculo de Preço Justo (Simples para o cliente entender)
                    preco_justo = (info.get('trailingAnnualDividendRate', 0) / 0.06) if info.get('trailingAnnualDividendRate') else (atual * 1.12)
                    
                    # Layout de Preço (Atual em cima, Justo embaixo)
                    st.metric(t, f"R$ {atual:,.2f}", f"{((atual/hist.Open.iloc[0])-1)*100:.2f}%")
                    st.caption(f"🎯 **Preço Justo:** R$ {preco_justo:,.2f}")
                    
                    # Mentor IA - Linguagem Simples
                    tese = TESES.get(t, "Ativo selecionado para monitoramento técnico de preço e volume.")
                    st.info(f"**O que é?**\n{tese}")
                    
                    # Veredito de Cor
                    if atual < preco_justo:
                        st.success("💎 BOA PARA COMPRA")
                    else:
                        st.warning("⏳ ESPERE CAIR")

                    # Gráfico Sparkline Limpo
                    fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#ffaa00', width=3))])
                    fig.update_layout(template='plotly_dark', height=80, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False)
                    st.plotly_chart(fig, use_container_width=True, key=f"spark_{t}")
        st.divider() # Linha separadora entre categorias

# Exibição organizada por "Estantes"
exibir_categoria("🪙 MERCADO CRIPTO", monitor_cripto)
exibir_categoria("🌎 MERCADO INTERNACIONAL (BDR/ETF)", monitor_bdr)
exibir_categoria("🇧🇷 MERCADO BRASILEIRO (AÇÕES)", monitor_acoes)

# Auto-Refresh
time.sleep(60)
st.rerun()
