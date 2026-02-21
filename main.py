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

# 2. Motor de Busca Blindado (Fim do erro image_41549e.png)
@st.cache_data(ttl=20)
def buscar_v240(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        info = tk.info
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if h.empty: return None, None, 0, 0, 0, 5.60, False
        
        # Lógica Específica para Ações (Evita image_4144be.jpg no BTC)
        p_justo, dpa_proj, div_real = 0, 0, 0
        if not is_c:
            lpa = info.get('forwardEps', 0)
            vpa = info.get('bookValue', 0)
            p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            dpa_proj = info.get('dividendRate', 0)
            div_raw = info.get('dividendYield', 0)
            div_real = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw
        
        return h, info, div_real, dpa_proj, p_justo, usd_brl, is_c
    except: return None, None, 0, 0, 0, 5.60, False

# --- MEMÓRIA DO TERMINAL ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk_tg = st.text_input("Token Telegram:", type="password")
    cid_tg = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Análise de Decisão")
    
    with st.form("form_v240", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, PETR4, BTC):").upper().strip()
        p_ent = st.number_input("Preço de Entrada:", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo de Venda:", min_value=0.0, format="%.2f")
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Quantidade Ações:", min_value=0, step=1)
            v_brl = p_ent * q_a
            
        if st.form_submit_button("🚀 Analisar e Monitorar"):
            if t_in:
                if p_ent > 0 or p_alv > 0:
                    st.session_state.radar[t_in] = {
                        "p_in": p_ent, "alvo": p_alv, "v_brl": v_brl, "qtd": q_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                    }
                    st.session_state.consulta = None
                else:
                    st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Monitoramento"):
        st.session_state.radar = {}
        st.session_state.consulta = None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Lucro Real")

# SEÇÃO 1: CONSULTA (Prevenção de erro de variável indefinida)
if st.session_state.consulta:
    res = buscar_v240(st.session_state.consulta)
    if res[0] is not None:
        h_c, info_c, div_c, dpa_c, p_j, dolar, is_c = res
        p_atual = h_c['Close'].iloc[-1]
        moeda = "US$" if is_c else "R$"
        st.subheader(f"🔍 Decisão: {st.session_state.consulta}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Preço {moeda}", f"{p_atual:,.2f}")
        
        if not is_c:
            c2.metric("Preço Justo", f"R$ {p_j:,.2f}")
            c3.metric("DPA Projetado", f"R$ {dpa_c:,.2f}/ação")
            c4.metric("Div. Yield", f"{div_c:.2f}%")
        else:
            c2.metric("Cotação em R$", f"R$ {p_atual * dolar:,.2f}")
            c3.metric("Market Cap", f"US$ {info_c.get('marketCap', 0)/1e9:.1f}B")
            c4.metric("Volume 24h", f"US$ {info_c.get('volume', 0)/1e6:.1f}M")

        fig_c = go.Figure(data=[go.Candlestick(x=h_c.index, open=h_c.Open, high=h_c.High, low=h_c.Low, close=h_c.Close)])
        fig_c.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_c, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO (Blindado contra NameError)
if st.session_state.radar:
    for t_at, cfg in list(st.session_state.radar.items()):
        res_at = buscar_v240(t_at)
        if res_at[0] is not None:
            h, info, div, dpa, p_j, dolar, is_c = res_at
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # Calculadora de Lucro (image_25fe79.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            v_inv_total = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            lucro_brl = (u_totais * (p_agora * taxa)) - v_inv_total
            
            with st.expander(f"📈 VIGIANDO: {t_at}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                col1.metric("Cotação", f"{p_agora:,.2f}")
                col2.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}")
                if st.button(f"Parar {t_at}", key=f"st_{t_at}")
