import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (Mantendo o layout aprovado)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência e Proventos (Sincronizado com Mercado)
@st.cache_data(ttl=60)
def analisar_v590(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        total_pago_12m = div_hist.sum()
        
        # Periodicidade e Veredito
        freq = "Mensal" if len(div_hist) >= 10 else ("Semestral" if len(div_hist) >= 2 else "Anual")
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_12m": total_pago_12m, "freq": freq, "div_hist": div_hist,
            "setor": info.get('sector', 'N/A'), "roe": (info.get('returnOnEquity', 0) or 0) * 100
        }

        # Graham e Fundamentos
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Canais Técnicos (LTA/LTB)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA PERSISTENTE ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: GESTÃO E ALVO DE RENDA ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    obj_renda = st.number_input("Objetivo Renda Mensal (R$):", min_value=0.0, value=1000.0)
    
    with st.form("comando_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, GRND3, BTC):").upper().strip()
        p_avg = st.number_input("Preço de Compra (R$):", min_value=0.0)
        qtd = st.number_input("Quantidade:", min_value=0, step=1)
        p_alvo = st.number_input("Preço de Venda (Alvo):", min_value=0.0)
        
        c1, c2 = st.columns(2)
        if c1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta = t_in; st.rerun()
        if c2.form_submit_button("📈 Monitorar"):
            if t_in and p_avg > 0:
                st.session_state.radar[t_in] = {"p_in": p_avg, "qtd": qtd, "alvo": p_alv}
                st.session_state.consulta = t_in; st.rerun()

    if st.button("🗑️ Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. MONITORAMENTO (Cards com Lucro Estimado e Renda)
if st.session_state.radar:
    st.subheader("📋 Monitoramento e Patrimônio")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v590(t_at)
        if dat:
            lucro_pct = ((dat['pa'] / cfg['p_in']) - 1) * 100
            lucro_brl = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > 0 else 0
            renda_anual = dat['div_12m'] * cfg['qtd']
            
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{lucro_pct:.2f}%")
                if lucro_brl > 0: st.caption(f"💰 Lucro Alvo: R$ {lucro_brl:,.2f}")
                st.caption(f"📅 Renda Anual: R$ {renda_anual:,.2f}")
                if st.button(f"Sair {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. ÁREA DO MENTOR E SIMULADOR (R$ 1.000)
if st.session_state.consulta:
    d = analisar_v590(st.session_state.consulta)
    if d:
        st.divider()
        st.subheader(f"🔍 Nexus Intelligence: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
        c3.metric("Div. 12m", f"R$ {d['div_12m']:,.2f}")
        c4.metric("ROE", f"{d['roe']:.1f}%")
        
        # MENSAGEM DO MENTOR (Recuperada)
        if not d['is_c']:
            st.info(f"✅ **Mentor Nexus:** Ativo de {d['setor']} com pagamento **{d['freq']}**. "
                    f"Para ter renda de **R$ {obj_renda:,.2f}**, você precisa de {int(obj_renda/(d['div_12m']/12))} ações.")
        
        # Gráfico com Canais LTA/LTB (Recuperado)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1), name="Média 20d"))
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="LTA/Suporte")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="LTB/Resistência")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
