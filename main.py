import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Gestor Master", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Busca e Alerta
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_dados(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), usd_brl, is_c
    except: return None, 5.65, False

# --- INICIALIZAÇÃO DA MEMÓRIA ---
if 'radar' not in st.session_state:
    st.session_state.radar = {}

# --- SIDEBAR: CONTROLE DE ENTRADA ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Configurar Novo Alvo")
    
    # FORMULÁRIO PARA EVITAR QUE APAGUE AO DIGITAR
    with st.form("config_ativo", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):").upper().strip()
        
        # O formulário mantém os valores até você clicar no botão de enviar
        p_ent = st.number_input("Preço de Compra (R$ ou US$):", min_value=0.0, format="%.2f")
        p_alvo = st.number_input("Alvo para Alerta (R$ ou US$):", min_value=0.0, format="%.2f")
        v_inv = st.number_input("Valor Investido Total (R$):", min_value=0.0, step=100.0)
        
        submitted = st.form_submit_button("🚀 Confirmar para Monitoramento")
        
        if submitted and t_in:
            is_c = t_in in ["BTC", "XRP", "ETH", "SOL"]
            st.session_state.radar[t_in] = {
                "p_in": p_ent, "alvo": p_alvo, "v_brl": v_inv, "is_c": is_c
            }
            st.success(f"{t_in} adicionado!")

    st.divider()
    st.subheader("📋 Lista de Mensagens Ativa")
    for t_l in list(st.session_state.radar.keys()):
        st.write(f"• {t_l}")
    
    # NOVO BOTÃO PARA LIMPAR O MONITORAMENTO
    if st.button("🗑️ Limpar Monitoramento"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Monitoramento")

if not st.session_state.radar:
    st.info("Sistema aguardando ativos. Preencha o formulário ao lado para iniciar.")
else:
    for t_mon in list(st.session_state.radar.keys()):
        cfg = st.session_state.radar[t_mon]
        h, dolar, is_c = buscar_dados(t_mon)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if cfg["p_in"] > 0 else 0
            v_atual_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_atual_brl - cfg["v_brl"]
            
            with st.expander(f"📊 MONITORANDO: {t_mon}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    moeda = "US$" if is_c else "R$"
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}")
                with c3:
                    if cfg['alvo'] > 0:
                        v_no_alvo = u_totais * (cfg['alvo'] * taxa)
                        st.write(f"🎯 **Alvo:** {moeda} {cfg['alvo']:,.2f}")
                        st.write(f"💰 **Ganho no Alvo:** R$ {v_no_alvo - cfg['v_brl']:,.2f}")
                        
                        if p_agora >= cfg['alvo']:
                            st.error("🚨 ALVO ATINGIDO!")
                            enviar_alerta(tk, cid, f"🚨 ALERTA: {t_mon} atingiu o alvo de {moeda} {cfg['alvo']}!")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), template="plotly_white", xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_mon}")

time.sleep(30)
st.rerun()
