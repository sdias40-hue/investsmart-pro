import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface Limpa (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca e Mensageria (image_e1717f.jpg)
@st.cache_data(ttl=30)
def buscar_dados_v106(t):
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

# --- SIDEBAR: CONTROLE TOTAL ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Configurar Monitoramento")
    
    # RESOLUÇÃO DA CAUSA RAIZ: Campos fora de formulário mas com chaves fixas
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):", key="f_t").upper().strip()
    is_c = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_c:
        # Lógica Cripto: Valor Investido (image_259617.png)
        v_inv = st.number_input("Valor Investido (R$):", key="f_v", min_value=0.0)
        p_ent = st.number_input("Preço Compra (US$):", key="f_pc", min_value=0.0)
        p_alv = st.number_input("Alvo Venda (US$):", key="f_pa", min_value=0.0)
        qtd_a = 0
    else:
        # Lógica Ações: Quantidade (image_2615ba.png)
        p_ent = st.number_input("Preço Compra (R$):", key="f_pca", min_value=0.0)
        qtd_a = st.number_input("Quantidade de Ações:", key="f_q", min_value=0, step=1)
        p_alv = st.number_input("Alvo Venda (R$):", key="f_paa", min_value=0.0)
        v_inv = p_ent * qtd_a

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "is_c": is_c, "v_brl": v_inv, "p_in": p_ent, "alvo": p_alv, "qtd": qtd_a
                }
                st.rerun()
    with c2:
        if st.button("🧹 Limpar Campos"):
            # Volta o botão que limpa apenas a lateral (image_26f600.png)
            for k in ["f_t", "f_v", "f_pc", "f_pa", "f_pca", "f_q", "f_paa"]:
                st.session_state[k] = "" if k == "f_t" else 0.0
            st.rerun()

    st.divider()
    st.subheader("📋 Mensagens Ativas")
    for t_list in list(st.session_state.radar.keys()):
        st.write(f"🟢 {t_list}")
    
    if st.button("🗑️ Encerrar Todas as Mensagens"):
        # Novo botão para limpar a lista de monitoramento (image_275090.png)
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Monitoramento")

if not st.session_state.radar:
    st.info("Aguardando ativos. Configure na lateral para iniciar o vigia.")
else:
    for
