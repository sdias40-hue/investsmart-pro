import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Inteligência", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise Fundamentalista e Projeções
@st.cache_data(ttl=30)
def buscar_v220(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        info = tk.info
        h = tk.history(period="60d", interval="1d")
        
        # CÁLCULOS DE VALOR (Graham & Projeções)
        lpa = info.get('forwardEps', 0)
        vpa = info.get('bookValue', 0)
        p_justo = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
        
        # DPA Projetado (Dividendo por Ação)
        dpa_proj = info.get('dividendRate', 0) 
        div_raw = info.get('dividendYield', 0)
        div_real = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw
        
        return h, info, div_real, dpa_proj, p_justo, is_c
    except: return None, None, 0, 0, 0, False

# --- GESTÃO DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk_bot = st.text_input("Token Telegram:", type="password")
    cid_bot = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Análise de Decisão")
    
    with st.form("form_v220", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, PETR4, BTC):").upper().strip()
        p_ent = st.number_input("Preço de Entrada:", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo de Venda:", min_value=0.0, format="%.2f")
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Qtd Ações:", min_value=0, step=1)
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
st.title("🏛️ InvestSmart Pro | Terminal de Performance")

# SEÇÃO 1: CONSULTA FUNDAMENTALISTA (Onde você decide o Trade)
if st.session_state.consulta:
    t_c = st.session_state.consulta
    h_c, info_c, div_c, dpa_c, p_justo, is_c_c = buscar_v220(t_c)
    if h_c is not None and not h_c.empty:
        p_atual = h_c['Close'].iloc[-1]
        st.subheader(f"🔍 Decisão Estratégica: {t_c}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
        
        if not is_c_c:
            upside = ((p_justo/p_atual)-1)*100 if p_atual > 0 else 0
            c2.metric("Preço Justo", f"R$ {p_justo:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("DPA Projetado", f"R$ {dpa_c:,.2f}/ação")
            c4.metric("Div. Yield", f"{div_c:.2f}%")
            
            st.success(f"🤖 **Mentor Analista:** {t_c} ({info_c.get('sector', 'N/A')}). "
                       f"O Preço Justo de Graham indica que a ação está {'BARATA' if p_justo > p_atual else 'CARA'} "
                       f"em relação aos seus fundamentos. DPA de R$ {dpa_c:,.2f} garante renda no Swing Trade.")
        
        fig_c = go.Figure(data=[go.Candlestick(x=h_c.index, open=h_c.Open, high=h_c.High, low=h_c.Low, close=h_c.Close)])
        fig_c.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_c, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO (Sinais de Kendall)
if st.session_state.radar:
    st.subheader("📋 Trades em Monitoramento")
    for t_at, cfg in list(st.session_state.radar.items()):
        h, info, div, dpa, p_j, is_c = buscar_v220(t_at)
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            
            with st.expander(f"📈 VIGIANDO: {t_at}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                col1.metric("Cotação", f"{p_agora:,.2f}")
                if st.button(f"Encerrar {t_at}", key=f"st_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
                
                with col3:
                    st.subheader("🤖 Sinais Day Trade")
                    if p_agora <= sup * 1.01: st.success("🔥 COMPRA: Pullback no Suporte!")
                    elif p_agora >= res * 0.99: st.error("⚠️ VENDA: Resistência atingida!")
                    else: st.write(f"⚖️ Neutro. Suporte: {sup:,.2f} | Resistência: {res:,.2f}")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")
        st.divider()

time.sleep(30)
st.rerun()
