import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface (CORRIGIDO: image_e263c4.png)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência com Planejamento (Sincronizado image_e20629.png)
@st.cache_data(ttl=60)
def analisar_v560(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # Sincronização DY com Investidor10 (image_e20629.png)
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        dy_real = (div_hist.sum() / h['Close'].iloc[-1]) * 100 if not div_hist.empty else 0
        
        # Periodicidade para Planejamento (Mensal, Semestral, etc)
        freq = "Irregular"
        if not div_hist.empty:
            count = len(div_hist)
            if count >= 10: freq = "Mensal"
            elif 3 <= count <= 5: freq = "Trimestral"
            elif count == 2: freq = "Semestral"
            elif count == 1: freq = "Anual"

        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "dy": dy_real, "freq": freq, "setor": info.get('sector', 'N/A'),
            "div_hist": div_hist, "div_total": div_hist.sum()
        }

        # Blindagem JEPP34 e Graham (image_e20607.png)
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
        
        # Canais Técnicos LTA/LTB (image_4c07e0.png)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA PERSISTENTE ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_ativa' not in st.session_state: st.session_state.consulta_ativa = None

# --- SIDEBAR: COMANDO NEXUS ( image_4c1edf.png) ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    with st.form("comando_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        is_cripto = t_in in ["BTC", "ETH", "SOL", "XRP"]
        
        if is_cripto:
            val_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            p_compra = st.number_input("Preço Entrada (US$):", min_value=0.0, format="%.4f")
        else:
            p_compra = st.number_input("Preço Compra (R$):", min_value=0.0)
            qtd = st.number_input("Quantidade:", min_value=0, step=1)
        
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        c1, c2 = st.columns(2)
        if c1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta_ativa = t_in; st.rerun()
        if c2.form_submit_button("📈 Monitorar"):
            if t_in and p_compra > 0:
                st.session_state.radar[t_in] = {"p_in": p_compra, "alvo": alvo, "is_c": is_cripto}
                st.session_state.consulta_ativa = t_in; st.rerun()

# --- PAINEL PRINCIPAL ---
if st.session_state.radar:
    st.subheader("📋 Monitoramento Nexus")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v560(t_at)
        if dat:
            p_now = dat['pa']
            lucro = ((p_now / cfg['p_in']) - 1) * 100
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {p_now:,.2f}", f"{lucro:.2f}%")

if st.session_state.consulta_ativa:
    d = analisar_v560(st.session_state.consulta_ativa)
    if d:
        st.divider()
        st.subheader(f"🔍 Nexus Intelligence: {st.session_state.consulta_ativa}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
        c3.metric("Div. Yield (12m)", f"{d['dy']:.2f}%")
        c4.metric("Pagamento", d['freq'])
        
        # MENSAGEM DO MENTOR
        st.info(f"📅 **Nexus Planning:** Pagamento **{d['freq']}**. Total de R$ {d['div_total']:.2f} acumulado nos últimos 12 meses.")

        # Gráfico e Histórico (CORRIGIDO: image_e20d86.png)
        with st.container():
            col_g1, col_g2 = st.columns([1, 2])
            with col_g1:
                if not d["div_hist"].empty:
                    st.write("**Histórico de Proventos:**")
                    st.table(d["div_hist"].reset_index().rename(columns={'Date':'Data','Dividends':'Valor'}))
            with col_g2:
                fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
                fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1), name="Média 20d"))
                fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="LTA")
                fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="LTB")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
