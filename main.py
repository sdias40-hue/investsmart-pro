import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração Blindada (Correção do TypeError da image_41cf82)
st.set_page_config(page_title="InvestSmart Sandro Pro", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Inteligência e Notícias (Proteção contra KeyError image_42397b)
@st.cache_data(ttl=300)
def buscar_noticias_v360(t):
    try:
        tk = yf.Ticker(t)
        news = tk.news
        return [n for n in news if 'title' in n and 'link' in n][:3]
    except: return []

@st.cache_data(ttl=20)
def buscar_v360(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        # Recuperando Informações do Mentor (image_405914 e image_41bcc2)
        d = {"h": h, "info": info, "is_c": is_c, "dolar": usd_brl}
        if not is_c:
            lpa = info.get('forwardEps', 0)
            vpa = info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["div"] = (info.get('dividendYield', 0) or 0) * 100
            d["pl"] = info.get('forwardPE', 0)
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["setor"] = info.get('sector', 'N/A')
        return d
    except: return None

# --- MEMÓRIA DA SESSÃO ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO SANDRO ---
with st.sidebar:
    st.title("🛡️ Central Sandro Pro")
    tkn = st.text_input("Token Telegram:", type="password", key="tk_v360")
    cid = st.text_input("Seu ID:", value="8392660003", key="id_v360")
    
    with st.form("form_v360", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, ETH, JEPP34):").upper().strip()
        p_ent = st.number_input("Preço Entrada:", min_value=0.0)
        p_alv = st.number_input("Alvo Venda:", min_value=0.0)
        
        if st.form_submit_button("🚀 Executar"):
            if t_in:
                if p_ent > 0: st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv}
                else: st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Registro"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title(f"🏛️ InvestSmart Pro | Terminal Sandro Master")

if st.session_state.consulta:
    d = buscar_v360(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Análise Profissional: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if not d['is_c']:
            # Mentor com dados recuperados (image_405914)
            c2.metric("Preço Justo", f"R$ {d.get('pj', 0):,.2f}")
            c3.metric("P/L", f"{d.get('pl', 0):,.1f}")
            c4.metric("Div. Yield", f"{d.get('div', 0):.2f}%")
            st.info(f"🤖 **Mentor Analista:** Ativo do setor de {d.get('setor')}. ROE de {d.get('roe', 0):.1f}%.")
        else:
            c2.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            c3.metric("Cotação R$", f"R$ {pa * d['dolar']:,.2f}")
            st.warning("🤖 **Mentor:** Cripto em tendência. Cuidado com a volatilidade nas notícias abaixo.")

        # Notícias (Fim do SyntaxError da image_41c4db)
        st.write("📰 **Notícias Recentes:**")
        for n in buscar_noticias_v360(st.session_state.consulta):
            st.write(f"• [{n['title']}]({n['link']})")

        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)

# SEÇÃO DE MONITORAMENTO (Recuperando image_242d00)
if st.session_state.radar:
    st.divider()
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v360(t_at)
        if d_at:
            h, p_now = d_at['h'], d_at['h']['Close'].iloc[-1]
            sup, res = h['Low'].rolling(14).min().iloc[-1], h['High'].rolling(14).max().iloc[-1]
            with st.expander(f"📈 MONITORANDO: {t_at} | Preço: {p_now:,.2f}", expanded=True):
                col1, col2 = st.columns([1, 2])
                col1.metric("Variação", f"{((p_now/cfg['p_in'])-1)*100:.2f}%")
                with col2:
                    if p_now <= sup * 1.01: st.success("🔥 SINAL: Pullback no Suporte!")
                    elif p_now >= res * 0.99: st.error("⚠️ SINAL: Resistência atingida!")
                if st.button(f"Remover {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()

time.sleep(30)
st.rerun()
