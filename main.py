import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. CSS de Alto Contraste (Fim do problema das cores apagadas)
st.set_page_config(page_title="InvestSmart Pro | Terminal", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 28px !important; font-weight: bold; }
    div[data-testid="stMetricDelta"] { color: #ffffff !important; }
    .stInfo { background-color: #161b22; border: 1px solid #30363d; color: #e6edf3; }
    .stMetric { background-color: #0d1117; border: 1px solid #30363d; padding: 20px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Alerta e Teses
def enviar_alerta_telegram(token, chat_id, mensagem):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": mensagem}, timeout=5)
        except: pass

TESES = {
    "OHI": "🏘️ REIT de Saúde (EUA). Dono de hospitais e asilos. Renda muito sólida e previsível.",
    "JEPP34": "💵 Dividendos em Dólar. ETF que gera renda mensal constante através de opções.",
    "BBAS3": "🏦 Banco do Brasil. Foco em Agronegócio. Uma das melhores pagadoras de dividendos da B3.",
    "BTC-USD": "🪙 Bitcoin. O 'Ouro Digital'. Reserva de valor escassa contra a inflação global.",
    "TAEE11": "⚡ Transmissão de Energia. Receita fixa por contrato. O porto seguro dos dividendos."
}

# 3. Motor de Dados Ultra-Rápido
def buscar_dados_elite(t):
    try:
        t_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(t_search)
        # Pegamos 5 dias para calcular a média de dividendos recente
        hist = ticker.history(period="5d", interval="1h")
        return hist, ticker.info, ticker.dividends
    except: return None, None, None

# --- SIDEBAR: O CENTRO DE COMANDO DO CLIENTE ---
with st.sidebar:
    st.title("🔑 Licença Ativa")
    token_bot = st.text_input("Seu Token Telegram:", type="password")
    chat_id = st.text_input("Seu ID de Usuário:")
    
    st.divider()
    st.header("➕ Monitoramento Global")
    st.info("Digite qualquer código do mundo (Ex: AAPL, VALE3, ETH-USD)")
    add_manual = st.text_input("Adicionar Ativo ao Radar:").upper()

    st.divider()
    m_cripto = st.multiselect("🪙 Criptos:", ["BTC-USD", "ETH-USD", "SOL-USD"], ["BTC-USD"])
    m_bdr = st.multiselect("🌎 Internacionais (BDR/ETF):", ["OHI", "JEPP34", "IVVB11"], ["OHI", "JEPP34"])
    m_acoes = st.multiselect("🇧🇷 Ações Brasil:", ["BBAS3", "TAEE11", "VULC3", "PETR4"], ["BBAS3", "TAEE11"])

    if st.button("🚀 ATIVAR MONITORAMENTO"):
        st.session_state.run = True
        enviar_alerta_telegram(token_bot, chat_id, "✅ Terminal InvestSmart Conectado!")

# --- PAINEL PRINCIPAL: ESTILO INVESTIDOR 10 ---
st.title("🏛️ InvestSmart Pro | Central de Renda e Análise")

def exibir_categoria_premium(titulo, lista):
    if add_manual and titulo == "🇧🇷 MERCADO BRASILEIRO (AÇÕES)":
        if add_manual not in lista: lista.append(add_manual)
    
    if lista:
        st.subheader(titulo)
        cols = st.columns(len(lista))
        for i, t in enumerate(lista):
            with cols[i]:
                hist, info, divs = buscar_dados_elite(t)
                if hist is not None and not hist.empty:
                    atual = hist['Close'].iloc[-1]
                    var = ((atual/hist['Open'].iloc[0])-1)*100
                    
                    # --- LOGICA DE DIVIDENDOS (Melhorada) ---
                    # Soma os dividendos do último ano (trailing)
                    dy_valor = info.get('trailingAnnualDividendRate', 0)
                    yield_p = info.get('trailingAnnualDividendYield', 0) * 100
                    preco_justo = (dy_valor / 0.06) if dy_valor > 0 else (atual * 1.10)

                    # Card Visual (Fim da cor apagada)
                    st.metric(f"💎 {t}", f"R$ {atual:,.2f}", f"{var:.2f}%")
                    
                    st.write(f"🎯 **Preço Justo:** R$ {preco_justo:,.2f}")
                    if dy_valor > 0:
                        st.write(f"📅 **Dividendos (12m):** R$ {dy_valor:,.2f} ({yield_p:.2f}%)")
                    else:
                        st.write("📅 **Dividendos:** Empresa de Crescimento")

                    # Mentor IA (Foco no Setor e Solidez)
                    tese = TESES.get(t, f"Ativo do setor de {info.get('sector', 'Mercado Global')}. Produto com base de ativos sólida e histórico em análise.")
                    st.info(f"**Análise:** {tese}")
                    
                    # Alerta Automático
                    if atual < preco_justo: st.success("✅ OPORTUNIDADE DE COMPRA")
                    else: st.warning("⏳ AGUARDE VALORIZAÇÃO")

                    # Mini Gráfico de Tendência
                    fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#00ff88', width=2))])
                    fig.update_layout(template='plotly_dark', height=70, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True, key=f"gr_{t}")
        st.divider()

# Exibição organizada como no exemplo do Investidor10
exibir_categoria_premium("🪙 MERCADO CRIPTO", m_cripto)
exibir_categoria_premium("🌎 MERCADO INTERNACIONAL (BDR/REIT/ETF)", m_bdr)
exibir_categoria_premium("🇧🇷 MERCADO BRASILEIRO (AÇÕES)", m_acoes)

time.sleep(60)
st.rerun()
