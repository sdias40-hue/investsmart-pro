import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Blindada
st.set_page_config(page_title="Sandro Portfolio Cloud", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise Híbrido (Ações, ETFs e Cripto)
@st.cache_data(ttl=60)
def analisar_v410(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # Correção Escala Dividendo
        div_raw = info.get('dividendYield', 0) or info.get('yield', 0) or 0
        div_final = (div_raw * 100) if (div_raw and div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up,
            "div": div_final, "pa": h['Close'].iloc[-1],
            "setor": info.get('sector', 'ETF/Renda'),
            "tipo": info.get('quoteType', 'EQUITY')
        }

        # Lógica para evitar travamento (JEPP34, RILYT)
        lpa = info.get('forwardEps')
        vpa = info.get('bookValue')
        if lpa and vpa and not is_c:
            d["pj"] = np.sqrt(22.5 * lpa * vpa)
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
        else:
            d["pj"], d["roe"] = 0, 0
            
        # Médias e Tendência
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(20).min()
        d["res"] = h['High'].tail(20).max()
        
        return d
    except: return None

# --- INICIALIZAÇÃO DE MEMÓRIA DE CARTEIRA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: GESTÃO DE ATIVOS ---
with st.sidebar:
    st.title("🛡️ Sandro Portfolio")
    with st.form("form_v410", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, JEPP34, BTC):").upper().strip()
        p_ent = st.number_input("Preço de Compra:", min_value=0.0, format="%.2f")
        qtd = st.number_input("Quantidade:", min_value=0, step=1)
        p_alv = st.number_input("Alvo de Venda:", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("🚀 Adicionar à Carteira"):
            if t_in and p_ent > 0:
                st.session_state.radar[t_in] = {"p_in": p_ent, "qtd": qtd, "alvo": p_alv}
                st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal Sandro Master | Gestão 24h")

# 1. MONITORAMENTO DE CARTEIRA (O que faltava)
if st.session_state.radar:
    st.subheader("📋 Minha Carteira Ativa")
    for t_at, cfg in list(st.session_state.radar.items()):
        dat = analisar_v410(t_at)
        if dat:
            p_now = dat['pa']
            lucro_pct = ((p_now / cfg['p_in']) - 1) * 100
            total_invest = cfg['p_in'] * cfg['qtd']
            lucro_brl = (p_now - cfg['p_in']) * cfg['qtd']
            
            with st.expander(f"📈 {t_at} | Lucro: {lucro_pct:.2f}% | R$ {lucro_brl:,.2f}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Preço Atual", f"{p_now:,.2f}")
                c2.metric("Quantidade", cfg['qtd'])
                c3.metric("Alvo de Venda", f"{cfg['alvo']:,.2f}")
                c4.metric("Patrimônio", f"R$ {p_now * cfg['qtd']:,.2f}")
                
                if cfg['alvo'] > 0 and p_now >= cfg['alvo']:
                    st.error(f"🎯 ALVO ATINGIDO EM {t_at}! Hora de realizar lucro.")
                
                if st.button(f"Remover {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
    st.divider()

# 2. ANÁLISE DETALHADA (Mentor)
if st.session_state.consulta:
    d = analisar_v410(st.session_state.consulta)
    if d:
        st.subheader(f"🔍 Veredito: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço", f"{d['pa']:,.2f}")
        
        if not d['is_c'] and d['pj'] > 0:
            c2.metric("Preço Justo", f"{d['pj']:,.2f}")
            c3.metric("Div. Yield", f"{d['div']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
        else:
            c2.metric("Yield", f"{d['div']:.2f}%")
            c3.metric("Suporte", f"{d['sup']:,.2f}")
            c4.metric("Resistência", f"{d['res']:,.2f}")

        # Gráfico com Tendências
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1), name="Média 20d"))
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="LTA/Suporte")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="LTB/Resistência")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
