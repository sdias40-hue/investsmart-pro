import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Setup de Interface (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise Especializado (Ação vs Cripto)
@st.cache_data(ttl=20)
def buscar_v230(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        # Busca correta: Cripto sempre em USD para evitar erro de escala (image_4144be.jpg)
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        info = tk.info
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        # Lógica de Dividendos e Preço Justo (Apenas para Ações)
        lpa = info.get('forwardEps', 0)
        vpa = info.get('bookValue', 0)
        p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 and not is_c else 0
        dpa_proj = info.get('dividendRate', 0) if not is_c else 0
        div_raw = info.get('dividendYield', 0)
        div_real = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw if not is_c else 0
        
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
    
    with st.form("form_v230", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, PETR4, BTC):").upper().strip()
        p_ent = st.number_input("Preço de Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo de Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
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

# SEÇÃO 1: CONSULTA ESPECIALIZADA
if st.session_state.consulta:
    t_c = st.session_state.consulta
    h_c, info_c, div_c, dpa_c, p_j, dolar, is_c = buscar_v230(t_c)
    if h_c is not None and not h_c.empty:
        p_atual = h_c['Close'].iloc[-1]
        moeda = "US$" if is_c else "R$"
        st.subheader(f"🔍 Análise de {t_c} ({'Cripto' if is_c else 'Ação'})")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Preço {moeda}", f"{moeda} {p_atual:,.2f}")
        
        if not is_c:
            c2.metric("Preço Justo", f"R$ {p_j:,.2f}")
            c3.metric("DPA Projetado", f"R$ {dpa_c:,.2f}/ação")
            c4.metric("Div. Yield", f"{div_c:.2f}%")
        else:
            # Dados específicos para Cripto (Fim do erro image_4144be.jpg)
            m_cap = info_c.get('marketCap', 0) / 1e9
            c2.metric("Market Cap", f"US$ {m_cap:.1f}B")
            c3.metric("Cotação em R$", f"R$ {p_atual * dolar:,.2f}")
            c4.metric("Moeda Base", "Dólar (USD)")
            st.info(f"🤖 **Mentor:** {t_c} é monitorado em Dólar. O valor em Reais é de aproximadamente R$ {p_atual * dolar:,.2f}.")

        fig_c = go.Figure(data=[go.Candlestick(x=h_c.index, open=h_c.Open, high=h_c.High, low=h_c.Low, close=h_c.Close)])
        fig_c.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_c, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO
if st.session_state.radar:
    for t_at, cfg in list(st.session_state.radar.items()):
        h, info, div, dpa, p_j, dolar, is_c
