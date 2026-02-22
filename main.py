import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface
st.set_page_config(page_title="Sandro Analyst Cloud", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise com Linhas de Tendência (LTA/LTB)
@st.cache_data(ttl=60)
def analisar_v400(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d") # 90 dias para tendências melhores
        if h.empty: return None
        
        info = tk.info
        # Correção definitiva do Dividendo (image_4b1f9e.jpg)
        div_raw = info.get('dividendYield', 0)
        div_final = (div_raw * 100) if (div_raw and div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        # Cálculos de Tendência (LTA/LTB/Suporte)
        recent = h.tail(30)
        sup = recent['Low'].min()
        res = recent['High'].max()
        
        # Média Móvel de 20 períodos (Tendência Terciária/Curto Prazo)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up,
            "div": div_final, "setor": info.get('sector', 'N/A'),
            "roe": (info.get('returnOnEquity', 0) or 0) * 100,
            "pl": info.get('forwardPE', 0), "sup": sup, "res": res,
            "pa": h['Close'].iloc[-1]
        }
        
        lpa, vpa = info.get('forwardEps', 0), info.get('bookValue', 0)
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
        return d
    except: return None

# --- MEMÓRIA SANDRO ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Sandro Analyst Cloud")
    with st.form("form_v400", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, AMZO34, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada (Opcional):", min_value=0.0)
        if st.form_submit_button("🚀 Analisar Profissionalmente"):
            if t_in:
                if p_ent > 0: st.session_state.radar[t_in] = {"p_in": p_ent}
                st.session_state.consulta = t_in
                st.rerun()
    if st.button("🧹 Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal Sandro Master | Análise de Tendência")

# 1. PAINEL DE MONITORAMENTO (Fixado no Topo)
if st.session_state.radar:
    st.subheader("📋 Monitoramento Ativo")
    m_cols = st.columns(len(st.session_state.radar))
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v400(t_at)
        if dat:
            lucro = ((dat['pa'] / cfg['p_in']) - 1) * 100
            m_cols[i].metric(t_at, f"R$ {dat['pa']:,.2f}", f"{lucro:.2f}%")
    st.divider()

# 2. CONSULTA DETALHADA COM GRÁFICO PROFISSIONAL
if st.session_state.consulta:
    d = analisar_v400(st.session_state.consulta)
    if d:
        st.subheader(f"🔍 Veredito do Mentor: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{d['pa']:,.2f}")
        
        if not d['is_c']:
            upside = ((d['pj']/d['pa'])-1)*100 if d['pa'] > 0 else 0
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("Div. Yield", f"{d['div']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            
            # MENTOR DETALHADO (image_4b1f9e.jpg)
            tendencia = "ALTA" if d['pa'] > d['h']['MA20'].iloc[-1] else "BAIXA"
            msg_ment = f"✅ **Mentor Sandro:** Ativo de {d['setor']} com bons fundamentos (ROE {d['roe']:.1f}%). "
            msg_ment += f"Gráfico em tendência de {tendencia} acima da Média de 20 dias. "
            if d['pa'] <= d['sup'] * 1.02: msg_ment += "🔥 Ponto de compra por Pullback no Suporte!"
            st.info(msg_ment)

        # GRÁFICO COM LTA, LTB E CANAL (image_4b1f9e.jpg)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close, name="Preço")])
        
        # Adicionando Linhas de Suporte e Resistência (Horizontal)
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte (LTA)")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência (LTB)")
        
        # Adicionando Média Móvel (Tendência)
        fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1.5), name="Média 20d"))
        
        fig.update_layout(height=500, template='plotly_white', xaxis_rangeslider_visible=False, title=f"Tendência Primária e Secundária: {d['ticker']}")
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
