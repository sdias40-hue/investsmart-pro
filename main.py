import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Setup Visual "High Clarity" (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Suporte
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v95(t):
    try:
        t_up = t.upper().strip()
        is_crypto = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_crypto else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl
    except: return None, None, 5.65

# --- SIDEBAR: CENTRO DE COMANDO SEPARADO ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    if 'monitor_v95' not in st.session_state: st.session_state.monitor_v95 = {}
    
    st.divider()
    st.subheader("➕ Nova Consulta/Monitor")
    
    # Inputs com chaves dinâmicas para limpeza manual controlada
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):", key="f_ticker").upper().strip()
    is_c = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_c:
        v_invest = st.number_input("Investimento (R$):", key="f_v_inv", min_value=0.0)
        p_comp = st.number_input("Preço Compra (US$):", key="f_p_in", min_value=0.0)
        p_alvo = st.number_input("Preço Alvo (US$):", key="f_p_out", min_value=0.0)
        qtd = 0
    else:
        p_comp = st.number_input("Preço Compra (R$):", key="f_p_in_a", min_value=0.0)
        qtd = st.number_input("Quantidade Ações:", key="f_qtd", min_value=0, step=1)
        p_alvo = st.number_input("Alvo Venda (R$):", key="f_p_out_a", min_value=0.0)
        v_invest = p_comp * qtd

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.monitor_v95[t_in] = {
                    "is_c": is_c, "v_brl": v_invest, "p_in": p_comp, "alvo": p_alvo, "qtd": qtd
                }
                st.rerun()
    with c2:
        if st.button("🧹 Limpar Campos"):
            # Limpa apenas os campos da lateral, sem apagar o que já está sendo monitorado
            for k in ["f_ticker", "f_v_inv", "f_p_in", "f_p_out", "f_p_in_a", "f_qtd", "f_p_out_a"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

    st.divider()
    st.subheader("📋 Lista Ativa")
    for t in st.session_state.monitor_v95.keys():
        st.write(f"• {t}")

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Monitoramento em Tempo Real")

if not st.session_state.monitor_v95:
    st.info("Sistema Online. Adicione ativos na lateral para monitorar.")
else:
    # Cria uma cópia das chaves para permitir a exclusão durante o loop
    tickers = list(st.session_state.monitor_v95.keys())
    for t in tickers:
        cfg = st.session_state.monitor_v95[t]
        h, info, dolar = buscar_v95(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            moeda = "US$" if cfg["is_c"] else "R$"
            
            # Calculadora Precisa
            total_u = cfg["v_brl"] / (cfg["p_in"] * dolar) if cfg["is_c"] and cfg["p_in"] > 0 else cfg["qtd"]
            v_total_brl = total_u * (p_agora * (dolar if cfg["is_c"] else 1))
            lucro_brl = v_total_brl - (cfg["v_brl"] if cfg["is_c"] else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📊 MONITORANDO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    st.caption(f"Unidades: {total_u:.6f}")
                    # BOTAO INDIVIDUAL PARA PARAR MONITORAMENTO
                    if st.button(f"🗑️ Parar {t}", key=f"del_{t}"):
                        del st.session_state.monitor_v95[t]
                        st.rerun()

                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                
                with c3:
                    st.subheader("🤖 Mentor de Alvos")
                    if cfg['alvo'] > 0:
                        v_no_alvo = total_u * (cfg['alvo'] * (dolar if cfg["is_c"] else 1))
                        lucro_alvo = v_no_alvo - (cfg["v_brl"] if cfg["is_c"] else (cfg["p_in"] * cfg["qtd"]))
                        st.success(f"🎯 Alvo {moeda} {cfg['alvo']:,.2f} = Lucro de **R$ {lucro_alvo:,.2f}**.")
                        
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO!")
                            enviar_alerta(tk, cid, f"💰 VENDA: {t} atingiu o alvo de {moeda}{cfg['alvo']}! Lucro: R$ {lucro_brl:,.2f}")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"v95_{t}")
        st.divider()

time.sleep(30)
st.rerun()
