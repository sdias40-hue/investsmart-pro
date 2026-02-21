import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Busca e Inteligência Blindadas
@st.cache_data(ttl=20)
def buscar_v280(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if h.empty: return None
        
        # Filtro de Dados: Fundamentalista para Ações (image_405914.png)
        d = {"h": h, "info": tk.info, "dolar": usd_brl, "is_c": is_c}
        if not is_c:
            lpa = tk.info.get('forwardEps', 0)
            vpa = tk.info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["dpa"] = tk.info.get('dividendRate', 0)
            div_raw = tk.info.get('dividendYield', 0)
            d["div"] = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw
        return d
    except: return None

def enviar_msg(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

# --- ESTADOS DE MEMÓRIA (image_3172e1.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO CENTRAL (Resolve image_41ae5a.png) ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tkn = st.text_input("Token Telegram:", type="password", key="tk_bot_v280")
    cid = st.text_input("Seu ID:", value="8392660003", key="id_bot_v280")
    
    st.divider()
    st.subheader("🚀 Análise e Trade")
    
    with st.form("form_v280", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Qtd Ações:", min_value=0, step=1)
            v_inv = p_ent * q_a
            
        if st.form_submit_button("🚀 Analisar e Iniciar"):
            if t_in:
                if p_ent > 0 or p_alv > 0:
                    st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv, "v_brl": v_inv, "qtd": q_a}
                    st.session_state.consulta = None
                else: st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Monitoramento"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Inteligência")

# SEÇÃO 1: CONSULTA DE DECISÃO (Recuperando image_405914.png)
if st.session_state.consulta:
    d = buscar_v280(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        moeda = "US$" if d['is_c'] else "R$"
        st.subheader(f"🔍 Decisão Estratégica: {st.session_state.consulta}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Preço {moeda}", f"{pa:,.2f}")
        
        if not d['is_c']:
            # Dados Fundamentalistas (image_41bcc2.jpg)
            c2.metric("Preço Justo", f"R$ {d.get('pj',0):,.2f}", f"{((d.get('pj',0)/pa)-1)*100:.1f}% Potencial")
            c3.metric("DPA Projetado", f"R$ {d.get('dpa',0):,.2f}/ação")
            c4.metric("Div. Yield", f"{d.get('div',0):.2f}%")
            st.info(f"🤖 **Mentor Analista:** {st.session_state.consulta} pertence ao setor de {d['info'].get('sector', 'N/A')}. "
                    f"Com P/L de {d['info'].get('forwardPE', 0):,.1f}, o ativo apresenta margem de segurança de {((d.get('pj',0)/pa)-1)*100:.1f}%.")
        else:
            # Dados Cripto (image_41b920.png)
            c2.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            c3.metric("Cotação R$", f"R$ {pa * d['dolar']:,.2f}")
            c4.metric("Vol 24h", f"US$ {d['info
