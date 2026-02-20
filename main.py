import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Alerta Telegram
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v89(t):
    try:
        is_crypto = t.upper() in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t.upper()}-USD" if is_crypto else (f"{t.upper()}.SA" if "." not in t else t.upper())
        ticker = yf.Ticker(search)
        # Puxa o dólar em tempo real para a calculadora
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl
    except: return None, None, 5.50

# --- SIDEBAR: CENTRAL DE INTELIGÊNCIA ---
with st.sidebar:
    st.title("🛡️ Central de Inteligência")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("ID Telegram:", value="8392660003")
    
    if 'lista_monitor' not in st.session_state: st.session_state.lista_monitor = {}
    
    st.divider()
    t_in = st.text_input("Ativo (Ex: VULC3, BTC):").upper().strip()
    v_brl = st.number_input("Valor Investido (R$):", min_value=0.0, step=100.0)
    p_in = st.number_input("Preço de Compra (Unidade):", min_value=0.0)
    p_out = st.number_input("Preço Alvo (Venda):", min_value=0.0)
    
    if st.button("🚀 Iniciar Monitoramento"):
        if t_in:
            # CORREÇÃO: Nome da chave 'investido' fixado para evitar o KeyError
            st.session_state.lista_monitor[t_in] = {
                "investido": v_brl, 
                "compra": p_in, 
                "alvo": p_out
            }
            st.rerun()

    if st.button("🗑️ Limpar Radar"):
        st.session_state.lista_monitor = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Monitoramento Global 24h")

if not st.session_state.lista_monitor:
    st.info("Radar pronto. Adicione seus ativos para monitoramento 24h na nuvem.")
else:
    for t, cfg in st.session_state.lista_monitor.items():
        h, info, dolar = buscar_v89(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            is_usd = "-" in h.index.name or any(x in t.upper() for x in ["BTC", "XRP"])
            moeda = "US$" if is_usd else "R$"
            
            # Cálculo de Lucro Blindado contra erros
            inv = cfg.get("investido", 0)
            comp = cfg.get("compra", 1) # Evita divisão por zero
            alvo_p = cfg.get("alvo", 0)
            
            cotas = inv / (comp * dolar if is_usd else comp) if comp > 0 else 0
            v_atual_brl = cotas * (p_agora * dolar if is_usd else p_agora)
            lucro_brl = v_atual_brl - inv
            
            with st.expander(f"📊 MONITORANDO: {t} (Real-Time)", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    st.write(f"🪙 Possui: **{cotas:.6f}**")
                with c2:
                    st.metric("Lucro Hoje", f"R$ {lucro_brl:,.2f}", f"{((p_agora/comp)-1)*100:.2f}%")
                    st.write(f"💰 Valor Total: R$ {v_atual_brl:,.2f}")
                with c3:
                    st.subheader("🤖 Mentor Estratégico")
                    if alvo_p > 0:
                        alvo_brl = cotas * (alvo_p * dolar if is_usd else alvo_p)
                        st.info(f"🎯 No alvo de {moeda} {alvo_p:,.2f}, você terá **R$ {alvo_brl - inv:,.2f}** de lucro limpo.")
                        if p_agora >= alvo_p:
                            st.success("🚨 ALVO ATINGIDO! HORA DA VENDA!")
                            enviar_alerta(tk, cid, f"🚨 VENDA AGORA: {t} atingiu o alvo! Lucro: R$ {lucro_brl:,.2f}")

                # Gráfico com Zoom e Médias
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"v89_{t}")

time.sleep(30)
st.rerun()
