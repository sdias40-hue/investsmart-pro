import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup de Alta Performance (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Decision", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca e Análise Fundamentalista
@st.cache_data(ttl=15)
def buscar_v200(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- GESTÃO DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: CONSULTA OU TRADE ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk_tg = st.text_input("Token Telegram:", type="password")
    cid_tg = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Decisão de Investimento")
    
    with st.form("decision_form", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço de Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo de Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Quantidade Ações:", min_value=0, step=1)
            v_brl = p_ent * q_a
            
        if st.form_submit_button("🚀 Executar"):
            if t_in:
                # Se preencher valores, entra na lista de mensagens. Caso contrário, consulta rápida.
                if p_ent > 0 or p_alv > 0:
                    st.session_state.radar[t_in] = {
                        "p_in": p_ent, "alvo": p_alv, "v_brl": v_brl, "qtd": q_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                    }
                    st.session_state.consulta = None
                else:
                    st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Lista de Mensagens"):
        st.session_state.radar = {}
        st.session_state.consulta = None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Performance")

# SEÇÃO 1: CONSULTA RÁPIDA E FUNDAMENTALISTA (Onde você decide o Trade)
if st.session_state.consulta:
    t_c = st.session_state.consulta
    h_c, info_c, dolar_c, is_c_c = buscar_v200(t_c)
    if h_c is not None and not h_c.empty:
        with st.container():
            st.subheader(f"🔍 Análise de Decisão: {t_c}")
            c1, c2, c3, c4 = st.columns(4)
            p_atual = h_c['Close'].iloc[-1]
            c1.metric("Preço Atual", f"{p_atual:,.2f}")
            
            if not is_c_c:
                # Dados Fundamentalistas (image_3f7b60.jpg)
                c2.metric("P/L", f"{info_c.get('forwardPE', 0):,.2f}")
                c3.metric("Dividend Yield", f"{info_c.get('dividendYield', 0)*100:.2f}%")
                c4.metric("ROE", f"{info_c.get('returnOnEquity', 0)*100:.2f}%")
            else:
                c2.metric("Market Cap", f"US$ {info_c.get('marketCap', 0)/1e9:.1f}B")
                c3.metric("Volume 24h", f"US$ {info_c.get('volume', 0)/1e6:.1f}M")
            
            fig_c = go.Figure(data=[go.Candlestick(x=h_c.index, open=h_c.Open, high=h_c.High, low=h_c.Low, close=h_c.Close)])
            fig_c.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_c, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO (Lista de Mensagens)
if st.session_state.radar:
    st.subheader("📋 Monitoramento Ativo para Mensagens")
    for t_at, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_v200(t_at)
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # Linhas de Tendência (LTA/LTB) - image_3f7b60.jpg
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            lucro_brl = (u_totais * (p_agora * taxa)) - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📈 VIGIANDO: {t_at}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric("Preço", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with col2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}")
                with col3:
                    st.subheader("🤖 Mentor Trade Specialist")
                    if cfg['alvo'] > 0:
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 META ATINGIDA!")
                        else:
                            st.info(f"Falta {((cfg['alvo']/p_agora)-1)*100:.2f}% para o seu Gain.")
                    
                    if p_agora <= sup * 1.01: st.success("🔥 COMPRA: Pullback no Suporte!")
                    elif p_agora >= res * 0.99: st.error("⚠️ VENDA: Breakout na Resistência!")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="LTA / Suporte")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="LTB / Resistência")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")
        st.divider()

time.sleep(30)
st.rerun()
