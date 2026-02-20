import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface (Layout Limpo)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca Global
@st.cache_data(ttl=30)
def buscar_dados(t):
    try:
        t_up = t.upper().strip()
        # Lista de Criptos para busca em Dólar
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        
        ticker = yf.Ticker(search)
        hist = ticker.history(period="60d", interval="1d")
        
        # Puxa o câmbio do Dólar em tempo real
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if hist.empty: return None, 5.65, False
        return hist, usd_brl, is_c
    except:
        return None, 5.65, False

def enviar_telegram(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

# --- INICIALIZAÇÃO DO MONITOR ---
if 'radar' not in st.session_state:
    st.session_state.radar = {}

# --- SIDEBAR: CONSULTA E LISTA ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Adicionar Ativo")
    
    # Inputs com chaves fixas
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):", key="campo_t").upper().strip()
    
    # Lógica Dinâmica de Campos
    is_cripto_input = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_cripto_input:
        v_invest = st.number_input("Investimento (R$):", key="campo_v", min_value=0.0)
        p_ent = st.number_input("Preço Compra (US$):", key="campo_pc", min_value=0.0)
        p_alvo = st.number_input("Alvo Venda (US$):", key="campo_pa", min_value=0.0)
        qtd_a = 0
    else:
        p_ent = st.number_input("Preço Compra (R$):", key="campo_pa_a", min_value=0.0)
        qtd_a = st.number_input("Qtd Ações:", key="campo_q", min_value=0, step=1)
        p_alvo = st.number_input("Alvo Venda (R$):", key="campo_pv_a", min_value=0.0)
        v_invest = p_ent * qtd_a

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Monitorar"):
            if t_in:
                # Salva no estado da sessão para não perder ao limpar campos
                st.session_state.radar[t_in] = {
                    "tipo": "C" if is_cripto_input else "A",
                    "v_brl": v_invest,
                    "p_in": p_ent,
                    "alvo": p_alvo,
                    "qtd": qtd_a
                }
                st.rerun()
    with c2:
        if st.button("🧹 Limpar Campos"):
            # Limpa apenas os campos de texto da lateral
            st.session_state.campo_t = ""
            for k in ["campo_v", "campo_pc", "campo_pa", "campo_pa_a", "campo_q", "campo_pv_a"]:
                st.session_state[k] = 0.0
            st.rerun()

    st.divider()
    st.subheader("📋 Lista de Monitorização")
    for t_list in list(st.session_state.radar.keys()):
        st.write(f"• {t_list}")

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Multi-Ativos")

if not st.session_state.radar:
    st.info("Nenhum ativo em monitorização. Use a barra lateral para adicionar.")
else:
    # Itera sobre todos os ativos guardados no radar
    for t_ativo in list(st.session_state.radar.keys()):
        cfg = st.session_state.radar[t_ativo]
        h, dolar, is_c = buscar_dados(t_ativo)
        
        if h is not None:
            p_agora = h['Close'].iloc[-1]
            moeda = "US$" if is_c else "R$"
            
            # Cálculo de Cotas e Lucro
            if is_c:
                u_totais = cfg["v_brl"] / (cfg["p_in"] * dolar) if cfg["p_in"] > 0 else 0
                v_invest_brl = cfg["v_brl"]
            else:
                u_totais = cfg["qtd"]
                v_invest_brl = cfg["p_in"] * cfg["qtd"]
            
            v_atual_brl = u_totais * (p_agora * (dolar if is_c else 1))
            lucro_brl = v_atual_brl - v_invest_brl
            
            with st.expander(f"📊 MONITORANDO: {t_ativo}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    if st.button(f"🗑️ Parar {t_ativo}", key=f"del_{t_ativo}"):
                        del st.session_state.radar[t_ativo]
                        st.rerun()
                
                with col2:
                    color = "normal" if lucro_brl >= 0 else "inverse"
                    st.metric("Lucro Hoje (R$)", f"R$ {lucro_brl:,.2f}", delta_color=color)
                    st.caption(f"Investido: R$ {v_invest_brl:,.2f}")
                
                with col3:
                    st.subheader("🤖 Mentor Estratégico")
