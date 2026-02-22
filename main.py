import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface (Otimizada para Nuvem)
st.set_page_config(page_title="InvestSmart Cloud", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Inteligência e Notícias
@st.cache_data(ttl=300)
def buscar_noticias_v350(t):
    try:
        tk = yf.Ticker(t)
        return [n for n in tk.news if 'title' in n and 'link' in n][:3]
    except: return []

@st.cache_data(ttl=20)
def buscar_v350(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if h.empty: return None
        
        info = tk.info
        d = {"h": h, "info": info, "dolar": usd_brl, "is_c": is_c, "ticker": t_up}
        
        # Recuperando a Inteligência do Mentor
        if not is_c:
            lpa = info.get('forwardEps', 0)
            vpa = info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["div"] = (info.get('dividendYield', 0) or 0) * 100
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["setor"] = info.get('sector', 'N/A')
            d["pl"] = info.get('forwardPE', 0)
        return d
    except: return None

# --- MEMÓRIA PERMANENTE ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO CENTRAL ---
with st.sidebar:
    st.title("🛡️ Central Cloud 24h")
    tkn = st.text_input("Token Telegram:", type="password", key="tk_cloud")
    cid = st.text_input("Seu ID:", value="8392660003", key="id_cloud")
    
    with st.form("form_v350", clear_on_submit=True):
        t_in = st.text_input("Ticker (JEPP34, A1IV34, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada:", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo Venda:", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("🚀 Analisar e Iniciar"):
            if t_in:
                if p_ent > 0:
                    st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv}
                else: st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Lista"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Decision Master")

# SEÇÃO 1: CONSULTA DE DECISÃO (Mentor Analista Completo)
if st.session_state.consulta:
    d = buscar_v350(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Análise Profissional: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if not d['is_c']:
            upside = ((d['pj']/pa)-1)*100 if pa > 0 else 0
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("Div. Yield", f"{d['div']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            st.info(f"🤖 **Mentor Analista:** Ativo do setor de {d['setor']}. "
                    f"P/L atual de {d['pl']:.1f}. Margem de segurança de {upside:.1f}%.")
        else:
            c2.metric("Cotação R$", f"R$ {pa * d['dolar']:,.2f}")
            c3.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            st.warning("🤖 **Mentor:** Criptomoeda detectada. Foco em sinais técnicos de suporte.")

        news = buscar_noticias_v350(st.session_state.consulta if not d['is_c'] else f"{st.session_state.consulta}-USD")
        if news:
            st.write("📰 **Últimas Notícias:**")
            for n in news: st.write(f"• [{n['title']}]({n['link']})")
        
        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO
if st.session_state.radar:
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v330(t_at) # Ajustado para v350 internamente
        if d_at:
            h, p_now = d_at['h'], d_at['h']['Close'].iloc[-1]
            sup, res = h['Low'].rolling(14).min().iloc[-1], h['High'].rolling(14).max().iloc[-1]
            
            with st.expander(f"📈 VIGIANDO: {t_at} | Preço: {p_now:,.2f}", expanded=True):
                col1, col2 = st.columns([1, 2])
                col1.metric("Variação", f"{((p_now/cfg['p_in'])-1)*100:.2f}%")
                if st.button(f"Remover {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
                
                with col2:
                    if p_now <= sup * 1.015: st.success("🔥 SINAL: Pullback no Suporte!")
                    elif p_now >= res * 0.985: st.error("⚠️ SINAL: Resistência atingida!")
                
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green")
                fig.add_hline(y=res, line_dash="dash", line_color="red")
                fig.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")

time.sleep(45)
st.rerun()
