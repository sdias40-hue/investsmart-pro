import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup Visual Clarity
st.set_page_config(page_title="InvestSmart Pro | Global", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff !important; border-radius: 12px; padding: 15px; border: 1px solid #dee2e6; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v88(t):
    try:
        is_crypto = t.upper() in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t.upper()}-USD" if is_crypto else (f"{t.upper()}.SA" if "." not in t else t.upper())
        ticker = yf.Ticker(search)
        # Busca o Dólar atual para conversão
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl
    except: return None, None, 5.0 # Fallback dólar a 5.0 se falhar

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Central de Inteligência")
    token = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("ID Telegram:", value="8392660003")
    
    if 'lista_monitor' not in st.session_state: st.session_state.lista_monitor = {}
    
    st.divider()
    t_input = st.text_input("Ativo (Ex: BTC, VULC3):").upper().strip()
    valor_investido_brl = st.number_input("Quanto investiu em REAIS (R$):", min_value=0.0, step=50.0)
    p_compra_unidade = st.number_input("Preço de Compra (Unidade):", min_value=0.0, help="Preço da unidade no momento que comprou")
    p_alvo_venda = st.number_input("Preço Alvo (Venda):", min_value=0.0)
    
    if st.button("🚀 Iniciar Monitoramento Ativo"):
        if t_input:
            st.session_state.lista_monitor[t_input] = {
                "investido": valor_investido_brl,
                "compra": p_compra_unidade,
                "alvo": p_alvo_venda
            }
            st.rerun()

    if st.button("🗑️ Limpar Tudo"):
        st.session_state.lista_monitor = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Calculadora de Lucro Real")

if not st.session_state.lista_monitor:
    st.info("Aguardando seu primeiro investimento no radar lateral.")
else:
    for t, config in st.session_state.lista_monitor.items():
        h, info, dolar = buscar_v88(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            is_usd = "-" in h.index.name or any(x in t.upper() for x in ["BTC", "XRP", "ETH"])
            moeda = "US$" if is_usd else "R$"
            
            # --- CALCULADORA DE COTAS E LUCRO ---
            # Se for cripto, o preço de compra e venda está em dólar, mas o investido em Reais
            if is_usd:
                # Quantas moedas comprei? (Investido em R$ / (Preço compra em US$ * Dólar))
                cotas = config['investido'] / (config['compra'] * dolar) if config['compra'] > 0 else 0
                valor_atual_brl = cotas * (p_agora * dolar)
                lucro_brl = valor_atual_brl - config['investido']
                alvo_brl = cotas * (config['alvo'] * dolar)
            else:
                cotas = config['investido'] / config['compra'] if config['compra'] > 0 else 0
                valor_atual_brl = cotas * p_agora
                lucro_brl = valor_atual_brl - config['investido']
                alvo_brl = cotas * config['alvo']

            with st.expander(f"📈 MONITORANDO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    st.write(f"🪙 Você possui: **{cotas:.6f}** {t}")
                
                with c2:
                    st.metric("Lucro Estimado", f"R$ {lucro_brl:,.2f}", f"{((p_agora/config['compra'])-1)*100:.2f}%" if config['compra'] > 0 else "0%")
                    st.write(f"💰 Valor Hoje: R$ {valor_atual_brl:,.2f}")

                with c3:
                    st.subheader("🤖 Mentor Estratégico")
                    if config['alvo'] > 0:
                        lucro_no_alvo = alvo_brl - config['investido']
                        st.info(f"Ao atingir {moeda} {config['alvo']:,.2f}, seu lucro será de **R$ {lucro_no_alvo:,.2f}**.")
                        
                        if p_agora >= config['alvo']:
                            st.success("🚨 ALVO ATINGIDO! HORA DE REALIZAR O LUCRO!")
                            enviar_alerta(token, cid, f"🚨 ALERTA DE VENDA: {t} bateu o alvo! Seu lucro estimado é de R$ {lucro_no_alvo:,.2f}")

                    # Sugestão baseada em Kendall
                    ma9 = h['Close'].rolling(9).mean().iloc[-1]
                    if p_agora > ma9:
                        st.success("🚀 Kendall indica forte tendência de subida. Mantenha a posição.")
                    else:
                        st.warning("⚖️ O preço esfriou no curto prazo. Aguarde reação das médias.")

                # Gráfico com linha de alvo
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close, name='Candle')])
                if config['alvo'] > 0:
                    fig.add_hline(y=config['alvo'], line_dash="dot", line_color="green", annotation_text="ALVO DE VENDA")
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"v88_{t}")
        st.divider()

time.sleep(30)
st.rerun()
