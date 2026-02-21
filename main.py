import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface Blindada (Resolve image_41cf82.png)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motores de Inteligência e Notícias Seguras (Resolve image_42397b.png)
@st.cache_data(ttl=300)
def buscar_noticias_v340(t):
    try:
        tk = yf.Ticker(t)
        news = tk.news
        return [n for n in news if 'title' in n and 'link' in n][:3]
    except: return []

@st.cache_data(ttl=20)
def buscar_v340(t):
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
        
        if not is_c:
            lpa = info.get('forwardEps', 0)
            vpa = info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["dpa"] = info.get('dividendRate', 0)
            div_raw = info.get('dividendYield', 0)
            d["div"] = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw
        return d
    except: return None

# --- MEMÓRIA DO TERMINAL (image_3172e1.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO CENTRAL ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tkn = st.text_input("Token Telegram:", type="password", key="tk_v340")
    cid = st.text_input("Seu ID:", value="8392660003", key="id_v340")
    
    st.divider()
    st.subheader("🚀 Análise e Trade")
    
    with st.form("form_v340", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, ETH):").upper().strip()
        p_ent = st.number_input("Preço Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("🚀 Executar"):
            if t_in:
                if p_ent > 0:
                    st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]}
                    st.session_state.consulta = None
                else: st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Registro"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Inteligência de Mercado")

# SEÇÃO 1: CONSULTA DE DECISÃO (Dados Completos Fundamentalistas)
if st.session_state.consulta:
    d = buscar_v340(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Análise Profissional: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if not d['is_c']:
            c2.metric("Preço Justo", f"R$ {d.get('pj', 0):,.2f}")
            c3.metric("Div. Yield", f"{d.get('div', 0):.2f}%")
            c4.metric("P/L", f"{d['info'].get('forwardPE', 0):,.1f}")
            st.info(f"🤖 **Mentor:** Setor: {d['info'].get('sector', 'N/A')} | ROE: {d['info'].get('returnOnEquity', 0)*100:.1f}%")
        else:
            c2.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            c3.metric("Cotação R$", f"R$ {pa * d['dolar']:,.2f}")
            c4.metric("Vol 24h", f"US$ {d['info'].get('volume', 0)/1e6:.1f}M")

        st.subheader("📰 Notícias Recentes")
        news = buscar_noticias_v340(st.session_state.consulta if not d['is_c'] else f"{st.session_state.consulta}-USD")
        for n in news: st.write(f"• [{n['title']}]({n['link']})")

        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO
if st.session_state.radar:
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v340(t_at)
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
                    if p_now <= sup * 1.015: st.success("🔥 SINAL: Ponto de Compra (Suporte)!")
                    elif p_now >= res * 0.985: st.error("⚠️ SINAL: Ponto de Venda (Resistência)!")
                
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência")
                fig.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")

# Redução de carga (Resolve PC lento)
time.sleep(45)
st.rerun()
