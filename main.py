import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Layout High Clarity
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Busca e Alerta
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v92(t):
    try:
        t_up = t.upper().strip()
        is_crypto = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_crypto else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl
    except: return None, None, 5.60

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ Radar de Lucro")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    if 'monitor_v92' not in st.session_state: st.session_state.monitor_v92 = {}
    
    st.divider()
    # Campos de entrada com chaves dinâmicas para permitir limpeza total
    t_in = st.text_input("Ticker (Ex: VULC3, BTC):", key="t_in").upper().strip()
    v_inv = st.number_input("Valor para Investir (R$):", min_value=0.0, step=100.0, key="v_inv")
    p_compra = st.number_input("Preço Atual (Unidade):", min_value=0.0, key="p_compra", help="Preço em US$ para Cripto ou R$ para Ações")
    p_alvo = st.number_input("Alvo de Venda:", min_value=0.0, key="p_alvo", help="Em US$ para Cripto ou R$ para Ações")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Monitorar"):
            if t_in and v_inv > 0:
                st.session_state.monitor_v92[t_in] = {
                    "v_brl": v_inv,
                    "p_in": p_compra,
                    "alvo": p_alvo
                }
                st.rerun()
    with col2:
        if st.button("🗑️ Limpar Tudo"):
            st.session_state.monitor_v92 = {}
            # Força a limpeza dos campos de input
            for key in ["t_in", "v_inv", "p_compra", "p_alvo"]:
                st.session_state[key] = "" if "t_in" in key else 0.0
            st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Dashboard Online")

if not st.session_state.monitor_v92:
    st.info("Radar limpo. Adicione um ativo para ver a projeção de lucro em Reais.")
else:
    for t, cfg in st.session_state.monitor_v92.items():
        h, info, dolar = buscar_v92(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            is_usd = t.upper() in ["BTC", "XRP", "ETH", "SOL"]
            moeda = "US$" if is_usd else "R$"
            
            # CALCULADORA INTUITIVA
            inv_brl = cfg["v_brl"]
            p_ent_moeda = cfg["p_in"]
            p_alvo_moeda = cfg["alvo"]
            
            # Se for US$, converte o investimento para saber as cotas
            custo_em_brl = p_ent_moeda * (dolar if is_usd else 1)
            cotas = inv_brl / custo_em_brl if custo_em_brl > 0 else 0
            
            v_hoje_brl = cotas * (p_agora * (dolar if is_usd else 1))
            lucro_brl = v_hoje_brl - inv_brl
            
            with st.expander(f"📊 {t} - Monitoramento de Lucro", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    st.caption(f"🪙 Quantidade: {cotas:.6f}")
                with c2:
                    color = "normal" if lucro_brl >= 0 else "inverse"
                    st.metric("Lucro Atual (R$)", f"R$ {lucro_brl:,.2f}", delta_color=color)
                    st.write(f"💰 Total Hoje: R$ {v_hoje_brl:,.2f}")
                with c3:
                    st.subheader("🤖 Mentor de Alvo")
                    if p_alvo_moeda > 0:
                        lucro_no_alvo = (cotas * (p_alvo_moeda * (dolar if is_usd else 1))) - inv_brl
                        st.success(f"🎯 Se chegar em {moeda} {p_alvo_moeda:,.2f}, seu lucro será de **R$ {lucro_no_alvo:,.2f}**.")
                        if p_agora >= p_alvo_moeda:
                            st.warning("🚨 ALVO ATINGIDO! HORA DE VENDER!")
                            enviar_alerta(tk, cid, f"🚨 ALERTA: {t} atingiu {moeda}{p_alvo_moeda}! Lucro: R$ {lucro_brl:,.2f}")
                    
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{t}")
        st.divider()

time.sleep(30)
st.rerun()
