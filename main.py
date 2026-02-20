import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup Visual High Clarity (Fundo Claro)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca e Mensageria
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v102(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl, is_c
    except: return None, None, 5.65, False

# --- INICIALIZAÇÃO DE ESTADOS (Proteção contra erros de limpeza) ---
if 'monitor_ativo' not in st.session_state: 
    st.session_state.monitor_ativo = {}

# --- SIDEBAR: CONSULTA VS MONITORAMENTO ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Nova Consulta / Monitor")
    
    # Sistema de Inputs Dinâmicos (Sempre abrem vazios após o rerun)
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):").upper().strip()
    is_c_in = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_c_in:
        v_inv = st.number_input("Investir em R$:", min_value=0.0, step=100.0, key="v_cripto")
        p_ent = st.number_input("Preço Compra (US$):", min_value=0.0, key="p_cripto")
        p_alv = st.number_input("Alvo Venda (US$):", min_value=0.0, key="a_cripto")
        qtd_a = 0
    else:
        p_ent = st.number_input("Preço Compra (R$):", min_value=0.0, key="p_acao")
        qtd_a = st.number_input("Qtd Ações:", min_value=0, step=1, key="q_acao")
        p_alv = st.number_input("Alvo Venda (R$):", min_value=0.0, key="a_acao")
        v_inv = p_ent * qtd_a

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.monitor_ativo[t_in] = {
                    "is_c": is_c_in, "v_brl": v_inv, "p_in": p_ent, "alvo": p_alv, "qtd": qtd_a
                }
                st.rerun()
    with col2:
        if st.button("🧹 Limpar Campos"):
            # RESET SEGURO: Limpa a memória temporária da lateral sem travar o app
            st.rerun()

    st.divider()
    st.subheader("📋 Lista Ativa")
    for t_list in list(st.session_state.monitor_ativo.keys()):
        st.write(f"🟢 {t_list}")

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Multi-Ativos")

if not st.session_state.monitor_ativo:
    st.info("Aguardando ativos. Adicione um Ticker na lateral para iniciar o vigia.")
else:
    # Mostra todos os ativos monitorados em cascata
    for t_mon in list(st.session_state.monitor_ativo.keys()):
        cfg = st.session_state.monitor_ativo[t_mon]
        h, info, dolar, is_c = buscar_v102(t_mon)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            moeda = "US$" if is_c else "R$"
            
            # Calculadora de Lucro em Real (Garantindo precisão do seu investimento)
            taxa = dolar if is_c else 1.0
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c and cfg["p_in"] > 0 else cfg["qtd"]
            v_inv_brl = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            v_hoje_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_hoje_brl - v_inv_brl
            
            with st.expander(f"📊 MONITORANDO: {t_mon}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    if st.button(f"Parar {t_mon}", key=f"stop_{t_mon}"):
                        del st.session_state.monitor_ativo[t_mon]
                        st.rerun()
                with c2:
                    st.metric("Lucro Hoje (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with c3:
