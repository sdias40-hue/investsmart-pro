import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
from gtts import gTTS
import base64
import io

# 1. Configuração de Interface Otimizada
st.set_page_config(page_title="InvestSmart Pro | Voice", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Voz (Text-to-Speech)
def falar(texto):
    try:
        tts = gTTS(text=texto, lang='pt', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true" src="data:audio/mp3;base64,{b64}">'
        st.markdown(md, unsafe_allow_html=True)
    except: pass

# 3. Motor de Busca Blindado
@st.cache_data(ttl=60) # Aumentado para 60s para aliviar o PC
def buscar_v330(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        d = {"h": h, "info": info, "is_c": is_c, "dolar": usd_brl}
        if not is_c:
            lpa, vpa = info.get('forwardEps', 0), info.get('bookValue', 0)
            d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            d["div"] = (info.get('dividendYield', 0) or 0) * 100
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Central de Voz")
    with st.form("form_v330", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, ETH):").upper().strip()
        p_ent = st.number_input("Preço Entrada:", min_value=0.0)
        p_alv = st.number_input("Alvo Venda:", min_value=0.0)
        
        if st.form_submit_button("🚀 Analisar e Falar"):
            if t_in:
                if p_ent > 0:
                    st.session_state.radar[t_in] = {"p_in": p_ent, "alvo": p_alv}
                else:
                    st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Registro"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Voz")

# SEÇÃO 1: CONSULTA COM RESUMO POR ÁUDIO
if st.session_state.consulta:
    d = buscar_v330(st.session_state.consulta)
    if d:
        pa = d['h']['Close'].iloc[-1]
        st.subheader(f"🔍 Análise: {st.session_state.consulta}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Preço Atual", f"{pa:,.2f}")
        
        texto_voz = f"Analisando {st.session_state.consulta}. O preço atual é {pa:,.2f}."
        
        if not d['is_c']:
            c2.metric("Preço Justo", f"R$ {d.get('pj', 0):,.2f}")
            c3.metric("Div. Yield", f"{d.get('div', 0):.2f}%")
            texto_voz += f" O preço justo de Graham é {d.get('pj', 0):,.2f} reais."
        else:
            c2.metric("Cotação R$", f"R$ {pa * d['dolar']:,.2f}")
            c3.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            texto_voz += f" Cotação em reais está em {pa * d['dolar']:,.2f}."

        falar(texto_voz) # O robô fala os dados da consulta
        
        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)

# SEÇÃO 2: MONITORAMENTO ATIVO
if st.session_state.radar:
    st.divider()
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_v330(t_at)
        if d_at:
            p_now = d_at['h']['Close'].iloc[-1]
            sup = d_at['h']['Low'].rolling(14).min().iloc[-1]
            
            with st.expander(f"📈 VIGIANDO: {t_at} | Preço: {p_now:,.2f}", expanded=True):
                if p_now <= sup * 1.01:
                    st.success(f"🔥 SINAL DE COMPRA EM {t_at}!")
                    falar(f"Atenção Sandro! Ponto de compra detectado em {t_at}.")
                
                if st.button(f"Remover {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()

# Alívio para o processador (Lentidão)
time.sleep(45) 
st.rerun()
