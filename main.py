import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_True=True)

# 2. Motor de Busca e Notícias Blindado
@st.cache_data(ttl=300) # Cache maior para notícias
def buscar_noticias(t):
    try:
        tk = yf.Ticker(t)
        return tk.news[:3] # Retorna as 3 últimas notícias
    except: return []

@st.cache_data(ttl=20)
def buscar_v290(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if h.empty: return None
        
        # Filtro de Dados Fundamentalistas (image_405914.png)
        d = {"h": h, "info": tk.info, "dolar": usd_brl, "is_c": is_c, "ticker": t_up}
        if not is_c:
            lpa = tk.info.get('forwardEps', 0)
            vpa = tk.info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["dpa"] = tk.info.get('dividendRate', 0)
            div_raw = tk.info.get('dividendYield', 0)
            d["div"] = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO CENTRAL ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tkn = st.text_input("Token Telegram:", type="password", key="tk_v290")
    cid = st.text_input("Seu ID:", value="8392660003", key="id_v290")
    
    st.divider()
    st.subheader("🚀 Análise e Trade")
    
    with st.form("form_v290", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada:", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo Venda:", min_value=0.0, format="%.2f")
        
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

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Decision Master")

# SEÇÃO 1: CONSULTA DE DECISÃO (Recuperando image_41bcc2.jpg)
if st.session_state.consulta:
    d = buscar_v290(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Decisão Estratégica: {st.session_state.consulta}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if not d['is_c']:
            c2.metric("Preço Justo", f"R$ {d.get('pj', 0):,.2f}")
            c3.metric("P/L", f"{d['info'].get('forwardPE', 0):,.1f}")
            c4.metric("Div. Yield", f"{d.get('div', 0):.2f}%")
            st.info(f"🤖 **Mentor:** Setor: {d['info'].get('sector', 'N/A')} | ROE: {d['info'].get('returnOnEquity', 0)*100:.1f}%")
        else:
            c2.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            c3.metric("Cotação R$", f"R$ {pa * d['dolar']:,.2f}")
            c4.metric("Vol 24h", f"US$ {d['info'].get('volume', 0)/1e6:.1f}M")

        # ÚLTIMAS NOTÍCIAS (Novidade v290)
        st.subheader("📰 Notícias Recentes")
        news = buscar_noticias(st.session_state.consulta)
        if news:
            for n in news: st.write(f"🔗 [{n['title']}]({n['link']})")
        else: st.write("Nenhuma notícia recente encontrada.")

        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO
if st.session_state.radar:
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v290(t_at)
        if d_at:
            p_now = d_at['h']['Close'].iloc[-1]
            tx = d_at['dolar'] if d_at['is_c'] else 1.0
            u_tot = cfg["v_brl"] / (cfg["p_in"] * tx) if d_at['is_c'] else cfg["qtd"]
            lucro = (u_tot * (p_now * tx)) - (cfg["v_brl"] if d_at['is_c'] else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📈 MONITORANDO: {t_at}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                col1.metric("Preço", f"{p_now:,.2f}")
                col2.metric("Lucro R$", f"R$ {lucro:,.2f}")
                if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
                
                with col3:
                    st.subheader("📰 Notícias do Ativo")
                    news_at = buscar_noticias(t_at)
                    for n in news_at[:2]: st.write(f"• {n['title']}")

                fig = go.Figure(data=[go.Candlestick(x=d_at['h'].index, open=d_at['h'].Open, high=d_at['h'].High, low=d_at['h'].Low, close=d_at['h'].Close)])
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")

time.sleep(30)
st.rerun()
