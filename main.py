import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="InvestSmart Pro | Multi-Ativos", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Mensageria
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v94(t):
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
    st.title("🛡️ Painel de Controle")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    if 'monitor_v94' not in st.session_state: st.session_state.monitor_v94 = {}
    
    st.divider()
    # Chaves únicas para permitir a limpeza completa dos campos
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):", key="input_ticker").upper().strip()
    
    is_cripto = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_cripto:
        v_inv = st.number_input("Investimento em REAIS (R$):", min_value=0.0, step=100.0, key="input_v_inv")
        p_compra = st.number_input("Preço de Entrada (US$):", min_value=0.0, key="input_p_in")
        p_alvo = st.number_input("Alvo de Venda (US$):", min_value=0.0, key="input_p_alvo")
        qtd_acoes = 0
    else:
        p_compra = st.number_input("Preço da Ação (R$):", min_value=0.0, key="input_p_in_acao")
        qtd_acoes = st.number_input("Qtd de Ações:", min_value=0, step=1, key="input_qtd")
        p_alvo = st.number_input("Alvo de Venda (R$):", min_value=0.0, key="input_p_alvo_acao")
        v_inv = p_compra * qtd_acoes

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Adicionar Ativo"):
            if t_in:
                st.session_state.monitor_v94[t_in] = {
                    "is_cripto": is_cripto,
                    "v_brl": v_inv,
                    "p_in": p_compra,
                    "alvo": p_alvo,
                    "qtd": qtd_acoes
                }
                st.rerun()
    with col2:
        if st.button("🗑️ Limpar Tudo"):
            st.session_state.monitor_v94 = {}
            # Limpa os estados dos inputs
            for k in list(st.session_state.keys()):
                if "input_" in k: del st.session_state[k]
            st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Monitoramento em Tempo Real")

if not st.session_state.monitor_v94:
    st.info("Sistema Online. Adicione seus ativos para iniciar o monitoramento acumulativo.")
else:
    for t, cfg in st.session_state.monitor_v94.items():
        h, info, dolar = buscar_v94(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            moeda = "US$" if cfg["is_cripto"] else "R$"
            
            # CALCULADORA MULTI-ATIVOS
            if cfg["is_cripto"]:
                custo_brl = cfg["p_in"] * dolar
                total_cotas = cfg["v_brl"] / custo_brl if custo_brl > 0 else 0
            else:
                total_cotas = cfg["qtd"]
            
            v_inv_total = cfg["v_brl"] if cfg["is_cripto"] else (cfg["p_in"] * cfg["qtd"])
            v_hoje_brl = total_cotas * (p_agora * (dolar if cfg["is_cripto"] else 1))
            lucro_brl = v_hoje_brl - v_inv_total
            
            with st.expander(f"📊 MONITORANDO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    st.caption(f"Unidades: {total_cotas:.6f}")
                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with c3:
                    st.subheader("🤖 Mentor de Alvos")
                    if cfg['alvo'] > 0:
                        v_no_alvo = total_cotas * (cfg['alvo'] * (dolar if cfg["is_cripto"] else 1))
                        st.success(f"🎯 Alvo em {moeda} {cfg['alvo']:,.2f} = Lucro de **R$ {v_no_alvo - v_inv_total:,.2f}**.")
                        
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO!")
                            enviar_alerta(tk, cid, f"💰 VENDA: {t} atingiu o alvo de {moeda}{cfg['alvo']}! Lucro: R$ {lucro_brl:,.2f}")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"v94_{t}")
        st.divider()

time.sleep(30)
st.rerun()
