import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Layout High Clarity (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca e Mensagem
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v97(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl, is_c
    except: return None, None, 5.65, False

# --- SIDEBAR: CONSULTA E LISTA ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    if 'monitor_v97' not in st.session_state: st.session_state.monitor_v97 = {}
    
    st.divider()
    st.subheader("🔍 Nova Consulta/Monitor")
    
    # Sistema de inputs limpos (image_2615ba.png)
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):", key="f_t").upper().strip()
    is_c_in = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_c_in:
        v_inv = st.number_input("Investir em R$:", key="f_v", min_value=0.0)
        p_comp = st.number_input("Preço Compra US$:", key="f_pc", min_value=0.0)
        p_alvo = st.number_input("Alvo Venda US$:", key="f_pa", min_value=0.0)
        qtd = 0
    else:
        p_comp = st.number_input("Preço Compra R$:", key="f_pca", min_value=0.0)
        qtd = st.number_input("Qtd Ações:", key="f_q", min_value=0, step=1)
        p_alvo = st.number_input("Alvo Venda R$:", key="f_paa", min_value=0.0)
        v_inv = p_comp * qtd

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.monitor_v97[t_in] = {
                    "is_c": is_c_in, "v_brl": v_inv, "p_in": p_comp, "alvo": p_alvo, "qtd": qtd
                }
                st.rerun()
    with col2:
        if st.button("🧹 Limpar Campos"):
            # Limpa os campos da lateral sem dar erro de API (image_266b36.png)
            for k in ["f_t", "f_v", "f_pc", "f_pa", "f_pca", "f_q", "f_paa"]:
                if k in st.session_state: st.session_state[k] = "" if "f_t" in k else 0.0
            st.rerun()

    st.divider()
    st.subheader("📋 Lista de Monitoramento")
    for t_list in list(st.session_state.monitor_v97.keys()):
        st.write(f"• {t_list}")

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Monitoramento em Tempo Real")

if not st.session_state.monitor_v97:
    st.info("Radar pronto e limpo. Adicione ativos na lateral para vigiar lucros.")
else:
    for t_mon in list(st.session_state.monitor_v97.keys()):
        cfg = st.session_state.monitor_v97[t_mon]
        h, info, dolar, is_crypto = buscar_v97(t_mon)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            moeda = "US$" if is_crypto else "R$"
            
            # Calculadora de Lucro em Reais (image_25fe79.png)
            total_u = cfg["v_brl"] / (cfg["p_in"] * dolar) if is_crypto and cfg["p_in"] > 0 else cfg["qtd"]
            v_total_brl = total_u * (p_agora * (dolar if is_crypto else 1))
            v_invest_brl = cfg["v_brl"] if is_crypto else (cfg["p_in"] * cfg["qtd"])
            lucro_brl = v_total_brl - v_invest_brl
            
            with st.expander(f"📊 VIGIANDO: {t_mon}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    if st.button(f"🗑️ Parar {t_mon}", key=f"del_{t_mon}"):
                        del st.session_state.monitor_v97[t_mon]
                        st.rerun()

                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                    st.caption(f"Valor Hoje: R$ {v_total_brl:,.2f}")
                
                with c3:
                    st.subheader("🤖 Mentor Estratégico")
                    if cfg['alvo'] > 0:
                        v_alvo_brl = total_u * (cfg['alvo'] * (dolar if is_crypto else 1))
                        lucro_alvo = v_alvo_brl - v_invest_brl
                        st.success(f"🎯 Alvo {moeda} {cfg['alvo']:,.2f} = Lucro de **R$ {lucro_alvo:,.2f}**.")
                        
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO! HORA DE VENDER!")
                            enviar_alerta(tk, cid, f"💰 ALERTA VENDA: {t_mon} atingiu o alvo! Lucro estimado: R$ {lucro_brl:,.2f}")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{t_mon}")
        st.divider()

time.sleep(30)
st.rerun()
