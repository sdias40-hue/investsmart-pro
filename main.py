import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface (Otimizada para Celular/Nuvem)
st.set_page_config(page_title="InvestSmart Sandro Pro", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Inteligência Especializado (Ação vs ETF/BDR)
@st.cache_data(ttl=20)
def buscar_v370(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        # Estrutura de Dados Blindada (Fim do travamento JEPP34)
        d = {"h": h, "info": info, "dolar": usd_brl, "is_c": is_c, "ticker": t_up}
        
        # Identifica se é ETF (Ex: JEPP34) ou Ação (Ex: VULC3)
        is_etf = info.get('quoteType') == 'ETF' or "Equity Premium" in info.get('longName', '')
        
        if not is_c and not is_etf:
            lpa, vpa = info.get('forwardEps', 0), info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["pl"] = info.get('forwardPE', 0)
            d["div"] = (info.get('dividendYield', 0) or 0) * 100
            d["setor"] = info.get('sector', 'N/A')
            d["tipo"] = "Ação"
        elif is_etf:
            d["div"] = (info.get('yield', 0) or info.get('trailingAnnualDividendYield', 0) or 0) * 100
            d["setor"] = "ETF / Renda"
            d["tipo"] = "ETF"
            d["pj"], d["roe"], d["pl"] = 0, 0, 0
            
        return d
    except: return None

# --- MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO SANDRO ---
with st.sidebar:
    st.title("🛡️ Sandro Master Cloud")
    with st.form("form_v370", clear_on_submit=True):
        t_in = st.text_input("Ticker (JEPP34, VULC3, ETH):").upper().strip()
        p_ent = st.number_input("Preço Entrada:", min_value=0.0)
        p_alv = st.number_input("Alvo Venda:", min_value=0.0)
        
        if st.form_submit_button("🚀 Analisar e Iniciar"):
            if t_in:
                if p_ent > 0: st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv}
                else: st.session_state.consulta = t_in
                st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal de Inteligência Sandro Pro")

if st.session_state.consulta:
    d = buscar_v370(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Veredito do Mentor: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        if d.get("tipo") == "Ação":
            upside = ((d['pj']/pa)-1)*100 if pa > 0 else 0
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("Div. Yield", f"{d['div']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            
            # O MENTOR VOLTOU A FALAR (Veredito)
            if d['roe'] > 15 and upside > 10:
                st.success(f"✅ **VEREDITO:** Esta ação é **EXCELENTE**. ROE de {d['roe']:.1f}% indica alta rentabilidade e o preço está descontado.")
            elif d['roe'] < 10:
                st.warning(f"⚠️ **VEREDITO:** Cuidado. Rentabilidade (ROE) baixa. Verifique se há recuperação no setor de {d['setor']}.")
        
        elif d.get("tipo") == "ETF":
            c2.metric("Yield Estimado", f"{d['div']:.2f}%")
            c3.metric("Perfil", "Renda Passiva")
            st.info(f"🤖 **Mentor:** {st.session_state.consulta} é um ETF de {d['setor']}. Foco em dividendos mensais, não em Preço Justo.")

        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)

# SEÇÃO DE MONITORAMENTO (Radar)
if st.session_state.radar:
    st.divider()
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v370(t_at)
        if d_at:
            p_now = d_at['h']['Close'].iloc[-1]
            sup = d_at['h']['Low'].rolling(14).min().iloc[-1]
            with st.expander(f"📈 MONITORANDO: {t_at} | R$ {p_now:,.2f}", expanded=True):
                if p_now <= sup * 1.015:
                    st.success("🔥 ALERTA: Ponto de Pullback Detectado!")
                if st.button(f"Remover {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
