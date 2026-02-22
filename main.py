import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface
st.set_page_config(page_title="Sandro Master Cloud", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca Blindado (Fim do erro image_49c206.jpg)
@st.cache_data(ttl=60)
def buscar_v390(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # Correção Dividendo (image_405914.png)
        div_raw = info.get('dividendYield', 0)
        div_certo = (div_raw * 100) if (div_raw and div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up,
            "div": div_certo, "setor": info.get('sector', 'N/A'),
            "roe": (info.get('returnOnEquity', 0) or 0) * 100,
            "pl": info.get('forwardPE', 0)
        }
        
        lpa, vpa = info.get('forwardEps', 0), info.get('bookValue', 0)
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
        return d
    except: return None

# --- INICIALIZAÇÃO DE MEMÓRIA (image_3172e1.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: CONTROLE SANDRO ---
with st.sidebar:
    st.title("🛡️ Sandro Cloud Pro")
    with st.form("form_v390", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, AMZO34, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada (Opcional):", min_value=0.0)
        
        if st.form_submit_button("🚀 Analisar e Iniciar"):
            if t_in:
                if p_ent > 0:
                    st.session_state.radar[t_in] = {"p_in": p_ent}
                st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal Sandro Master Cloud")

# SEÇÃO 1: MONITORAMENTO FIXO (Sempre visível no topo - image_49c206.jpg)
if st.session_state.radar:
    st.subheader("📋 Monitoramento Ativo")
    cols = st.columns(len(st.session_state.radar))
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        d_at = buscar_v390(t_at)
        if d_at:
            p_now = d_at['h']['Close'].iloc[-1]
            lucro = ((p_now / cfg['p_in']) - 1) * 100
            cols[i].metric(t_at, f"R$ {p_now:,.2f}", f"{lucro:.2f}%")
    st.divider()

# SEÇÃO 2: CONSULTA DETALHADA (Veredito do Mentor)
if st.session_state.consulta:
    d = buscar_v390(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Veredito do Mentor: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if not d['is_c']:
            upside = ((d['pj']/pa)-1)*100 if pa > 0 else 0
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("Div. Yield", f"{d['div']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            
            # MENTOR PERSISTENTE (image_49c206.jpg)
            if d['roe'] > 15:
                st.success(f"✅ **Mentor Sandro:** Esta ação é **MUITO BOA**. Setor de {d['setor']}.")
            else:
                st.warning(f"⚠️ **Mentor Sandro:** Ativo em análise. Setor: {d['setor']}.")

        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)

time.sleep(30)
st.rerun()
