import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Layout High Clarity (Fundo Branco para máxima legibilidade)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 12px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #007bff !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Suporte Blindadas
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v91(t):
    try:
        # Força busca global para BTC e XRP para evitar erro de preço (US$ 67k real)
        criptos_globais = ["BTC", "XRP", "ETH", "SOL"]
        t_up = t.upper().strip()
        search = f"{t_up}-USD" if t_up in criptos_globais and "-" not in t_up else (t_up if ".SA" in t_up or "-" in t_up else f"{t_up}.SA")
        
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl
    except: return None, None, 5.50

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ Radar Estratégico")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    if 'monitor_v91' not in st.session_state: st.session_state.monitor_v90 = {} # Compatibilidade
    if 'monitor_ativo' not in st.session_state: st.session_state.monitor_ativo = {}
    
    st.divider()
    t_in = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
    v_investido = st.number_input("Valor Total Investido (R$):", min_value=0.0, step=100.0)
    p_compra = st.number_input("Preço de Compra Unitário:", min_value=0.0)
    p_alvo_venda = st.number_input("Preço Alvo de Venda:", min_value=0.0)
    
    if st.button("🚀 Iniciar Monitoramento"):
        if t_in:
            # FIX DEFINITIVO: Chaves protegidas para evitar KeyError
            st.session_state.monitor_ativo[t_in] = {
                "valor_investido": v_investido,
                "preco_entrada": p_compra,
                "alvo_saida": p_alvo_venda
            }
            st.rerun()

    if st.button("🗑️ Limpar Radar"):
        st.session_state.monitor_ativo = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Lucro Real")

if not st.session_state.monitor_ativo:
    st.info("Radar pronto. Adicione seus ativos na lateral para monitorar lucros e tendências.")
else:
    for t, cfg in st.session_state.monitor_ativo.items():
        h, info, dolar = buscar_v91(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            is_usd = "-" in h.index.name or any(x in t.upper() for x in ["BTC", "XRP"])
            moeda = "US$" if is_usd else "R$"
            
            # Calculadora de Lucro Protegida (Fim do SyntaxError e KeyError)
            v_inv = cfg.get("valor_investido", 0)
            p_ent = cfg.get("preco_entrada", 1)
            p_alvo = cfg.get("alvo_saida", 0)
            
            # Cálculo de cotas e valor atual convertido
            taxa_conv = dolar if is_usd else 1.0
            total_cotas = v_inv / (p_ent * taxa_conv) if p_ent > 0 else 0
            v_atual_brl = total_cotas * (p_agora * taxa_conv)
            lucro_brl = v_atual_brl - v_inv
            
            with st.expander(f"📊 MONITORANDO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    st.caption(f"🪙 Cotas: {total_cotas:.6f}")
                with c2:
                    st.metric("Lucro Hoje (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/p_ent)-1)*100:.2f}%" if p_ent > 0 else "0%")
                    st.caption(f"💰 Valor Total: R$ {v_atual_brl:,.2f}")
                with c3:
                    st.subheader("🤖 Mentor Estratégico")
                    if p_alvo > 0:
                        lucro_alvo_brl = (total_cotas * (p_alvo * taxa_conv)) - v_inv
                        st.info(f"🎯 Ao bater {moeda} {p_alvo:,.2f}, seu lucro será de **R$ {lucro_alvo_brl:,.2f}**.")
                        if p_agora >= p_alvo:
                            st.success("🚨 ALVO ATINGIDO! HORA DE REALIZAR O LUCRO!")
                            enviar_alerta(tk, cid, f"🚨 ALERTA VENDA: {t} atingiu o alvo! Lucro estimado: R$ {lucro_brl:,.2f}")

                # Gráfico Online (Kendall)
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"v91_{t}")
        st.divider()

time.sleep(30)
st.rerun()
