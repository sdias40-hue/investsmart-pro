import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Sandro Pro", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Inteligência e Notícias
@st.cache_data(ttl=60)
def buscar_v380(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        d = {"h": h, "info": info, "is_c": is_c, "ticker": t_up}
        
        # Identificação de Ativo (Evita travar JEPP34)
        is_etf = info.get('quoteType') == 'ETF' or "Equity Premium" in info.get('longName', '')
        
        if not is_c and not is_etf:
            lpa, vpa = info.get('forwardEps', 0), info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["div"] = (info.get('dividendYield', 0) or 0) * 100
            d["setor"] = info.get('sector', 'N/A')
            d["vpa"] = vpa
            d["lpa"] = lpa
        return d
    except: return None

# --- INICIALIZAÇÃO DE MEMÓRIA (Resolve o problema de sumir informações) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'ultima_consulta' not in st.session_state: st.session_state.ultima_consulta = None

# --- SIDEBAR: COMANDO SANDRO ---
with st.sidebar:
    st.title("🛡️ Sandro Cloud Pro")
    with st.form("form_v380", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: JEPP34, VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada:", min_value=0.0)
        p_alv = st.number_input("Alvo Venda:", min_value=0.0)
        
        if st.form_submit_button("🚀 Analisar e Iniciar"):
            if t_in:
                if p_ent > 0:
                    st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv}
                else:
                    # Trava a consulta na memória para não sumir
                    st.session_state.ultima_consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Registro"):
        st.session_state.radar, st.session_state.ultima_consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal de Inteligência Sandro Pro")

# EXIBIÇÃO DA CONSULTA PERSISTENTE
if st.session_state.ultima_consulta:
    d = buscar_v380(st.session_state.ultima_consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Veredito do Mentor: {st.session_state.ultima_consulta}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if not d['is_c'] and "pj" in d:
            upside = ((d['pj']/pa)-1)*100 if pa > 0 else 0
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("Dividend Yield", f"{d['div']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            
            # ANÁLISE SE É BOA (O que o Mentor se perdeu)
            if d['roe'] > 15 and d['lpa'] > 0:
                st.success(f"✅ **Mentor Sandro:** Esta ação é **MUITO BOA**. Ela entrega lucro real sobre o capital investido e pertence ao setor de {d['setor']}.")
            else:
                st.warning(f"⚠️ **Mentor Sandro:** Atenção. Ativo com margens apertadas. Verifique o setor de {d['setor']} antes de entrar.")
        
        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)

# LISTA DE MONITORAMENTO
if st.session_state.radar:
    st.divider()
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v380(t_at)
        if d_at:
            p_now = d_at['h']['Close'].iloc[-1]
            st.info(f"📈 Monitorando {t_at}: Preço atual R$ {p_now:,.2f}")
