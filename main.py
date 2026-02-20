import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface (Layout High Clarity - image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca Blindado
@st.cache_data(ttl=30)
def buscar_dados_v107(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), usd_brl, is_c
    except: return None, 5.65, False

def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

# --- INICIALIZAÇÃO DA MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: CONTROLE TOTAL (image_276754.png) ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Configurar Monitoramento")
    
    # Campo de Ticker Independente
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):", key="f_t").upper().strip()
    is_c = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    # Campos Adaptativos (image_275090.png)
    if is_c:
        v_inv = st.number_input("Valor Investido (R$):", key="f_v", min_value=0.0)
        p_ent = st.number_input("Preço Compra (US$):", key="f_pc", min_value=0.0)
        p_alv = st.number_input("Alvo Venda (US$):", key="f_pa", min_value=0.0)
        qtd_a = 0
    else:
        p_ent = st.number_input("Preço Compra (R$):", key="f_pca", min_value=0.0)
        qtd_a = st.number_input("Quantidade de Ações:", key="f_q", min_value=0, step=1)
        p_alv = st.number_input("Alvo Venda (R$):", key="f_paa", min_value=0.0)
        v_inv = p_ent * qtd_a

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "is_c": is_c, "v_brl": v_inv, "p_in": p_ent, "alvo": p_alv, "qtd": qtd_a
                }
                st.rerun()
    with col2:
        if st.button("🧹 Limpar Campos"):
            for k in ["f_t", "f_v", "f_pc", "f_pa", "f_pca", "f_q", "f_paa"]:
                st.session_state[k] = "" if k == "f_t" else 0.0
            st.rerun()

    st.divider()
    st.subheader("📋 Mensagens Ativas")
    for t_list in list(st.session_state.radar.keys()):
        st.write(f"🟢 {t_list}")
    
    if st.button("🗑️ Limpar Monitoramento"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Lucro Real")

if not st.session_state.radar:
    st.info("Sistema Online. Adicione seus ativos na lateral para vigiar.")
else:
    for t_at in list(st.session_state.radar.keys()):
        cfg = st.session_state.radar[t_at]
        h, dolar, is_c = buscar_dados_v107(t_at)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            moeda = "US$" if is_c else "R$"
            
            # Calculadora de Lucro (image_25fe79.png)
            taxa = dolar if is_c else 1.0
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c and cfg["p_in"] > 0 else cfg["qtd"]
            v_inv_brl = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            v_hoje_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_hoje_brl - v_inv_brl
            
            with st.expander(f"📊 MONITORANDO: {t_at}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with c3:
                    st.subheader("🤖 Mentor")
                    if cfg['alvo'] > 0:
                        v_alvo_brl = u_totais * (cfg['alvo'] * taxa)
                        st.success(f"🎯 Alvo {moeda} {cfg['alvo']:,.2f} = Lucro de R$ {v_alvo_brl - v_inv_brl:,.2f}")
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO!")
                            enviar_alerta(tk, cid, f"💰 VENDA: {t_at
