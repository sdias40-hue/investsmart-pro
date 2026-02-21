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
def buscar_noticias_v320(t):
    try:
        tk = yf.Ticker(t)
        news = tk.news
        if not news: return []
        # Filtra apenas notícias que possuem título e link para não dar erro
        return [n for n in news if 'title' in n and 'link' in n][:3]
    except: return []

@st.cache_data(ttl=20)
def buscar_v320(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL", "ETH-USD", "BTC-USD"]
        search = f"{t_up}-USD" if (is_c and "-USD" not in t_up) else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if h.empty: return None
        
        # Filtro de Dados (image_41bcc2.jpg e image_41b920.png)
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

# --- MEMÓRIA DO TERMINAL ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO CENTRAL ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tkn = st.text_input("Token Telegram:", type="password", key="tk_v320")
    cid = st.text_input("Seu ID:", value="8392660003", key="id_v320")
    
    st.divider()
    st.subheader("🚀 Análise e Trade")
    
    with st.form("form_v320", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, ETH, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada:", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo Venda:", min_value=0.0, format="%.2f")
        
        is_cripto = t_in in ["BTC", "XRP", "ETH", "SOL"]
        if is_cripto:
            v_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Qtd Ações:", min_value=0, step=1)
            v_inv = p_ent * q_a
            
        if st.form_submit_button("🚀 Analisar e Iniciar"):
            if t_in:
                if p_ent > 0:
                    st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv, "v_brl": v_inv, "qtd": q_a, "is_c": is_cripto}
                    st.session_state.consulta = None
                else: st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Lista"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Inteligência de Mercado")

# SEÇÃO 1: CONSULTA DE DECISÃO (Resolução definitiva para o erro de notícias)
if st.session_state.consulta:
    d = buscar_v320(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Decisão Estratégica: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if not d['is_c']:
            c2.metric("Preço Justo", f"R$ {d.get('pj', 0):,.2f}")
            c3.metric("DPA Projetado", f"R$ {d.get('dpa',0):,.2f}/ação")
            c4.metric("Div. Yield", f"{d.get('div', 0):.2f}%")
        else:
            c2.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            c3.metric("Cotação R$", f"R$ {pa * d['dolar']:,.2f}")
            c4.metric("Vol 24h", f"US$ {d['info'].get('volume', 0)/1e6:.1f}M")

        # NOTÍCIAS BLINDADAS (Não dá mais KeyError)
        st.subheader("📰 Notícias Recentes")
        news_list = buscar_noticias_v320(st.session_state.consulta if not d['is_c'] else f"{st.session_state.consulta}-USD")
        if news_list:
            for n in news_list: st.write(f"• [{n['title']}]({n['link']})")
        else: st.write("Nenhuma notícia encontrada no momento.")

        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO
if st.session_state.radar:
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v320(t_at)
        if d_at:
            h, p_now = d_at['h'], d_at['h']['Close'].iloc[-1]
            tx = d_at['dolar'] if d_at['is_c'] else 1.0
            u_tot = cfg["v_brl"] / (cfg["p_in"] * tx) if d_at['is_c'] else cfg["qtd"]
            lucro = (u_tot * (p_now * tx)) - (cfg["v_brl"] if d_at['is_c'] else (cfg["p_in"] * cfg["qtd"]))
            sup, res = h['Low'].rolling(14).min().iloc[-1], h['High'].rolling(14).max().iloc[-1]
            
            with st.expander(f"📈 VIGIANDO: {t_at} | R$ {lucro:,.2f}", expanded=True):
                col1, col2 = st.columns([1, 2])
                col1.metric("Preço", f"{p_now:,.2f}", f"{((p_now/cfg['p_in'])-1)*100:.2f}%")
                if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
                
                with col2:
                    st.write(f"🎯 Alvo: {cfg['alvo']:,.2f} | 🟢 Suporte: {sup:,.2f} | 🔴 Resistência: {res:,.2f}")
                
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green")
                fig.add_hline(y=res, line_dash="dash", line_color="red")
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")

time.sleep(30)
st.rerun()
