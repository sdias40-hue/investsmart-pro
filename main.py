import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface
st.set_page_config(page_title="Sandro Cloud Pro", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise Blindado (Correção RILYT e JEPP34)
@st.cache_data(ttl=60)
def analisar_v440(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # Escala de Dividendos Corrigida
        div_raw = info.get('dividendYield', 0) or info.get('yield', 0) or 0
        div_real = (div_raw * 100) if (div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_m": div_real / 12, "div_a": div_real,
            "setor": info.get('sector', 'ETF / Renda Fixa / BDR')
        }

        # BLINDAGEM TOTAL: Só calcula fundamentos se os dados existirem (Evita travamento RILYT)
        lpa = info.get('forwardEps')
        vpa = info.get('bookValue')
        if lpa and vpa and not is_c and info.get('quoteType') == 'EQUITY':
            d["pj"] = np.sqrt(22.5 * lpa * vpa)
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["tem_fundamentos"] = True
        else:
            d["pj"], d["roe"], d["tem_fundamentos"] = 0, 0, False
        
        # Canais Técnicos (LTA/LTB)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup_lta"] = h['Low'].tail(30).min()
        d["res_ltb"] = h['High'].tail(30).max()
        return d
    except Exception as e:
        return None

# --- MEMÓRIA SANDRO ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_fixa' not in st.session_state: st.session_state.consulta_fixa = None

# --- SIDEBAR: GESTÃO ---
with st.sidebar:
    st.title("🛡️ Sandro Cloud Pro")
    with st.form("comando_master", clear_on_submit=False):
        t_in = st.text_input("Ticker:", value=st.session_state.consulta_fixa or "").upper().strip()
        
        is_c_check = t_in in ["BTC", "ETH", "SOL", "XRP"]
        if is_c_check:
            val_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            p_compra = st.number_input("Preço de Entrada (US$):", min_value=0.0)
        else:
            p_compra = st.number_input("Preço de Compra (R$):", min_value=0.0)
            qtd = st.number_input("Quantidade:", min_value=0, step=1)
        
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        col_b1, col_b2 = st.columns(2)
        if col_b1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta_fixa = t_in; st.rerun()
        if col_b2.form_submit_button("📈 Monitorar"):
            if t_in and p_compra > 0:
                st.session_state.radar[t_in] = {"p_in": p_compra, "alvo": alvo, "is_c": is_c_check}
                st.session_state.consulta_fixa = t_in; st.rerun()

# --- PAINEL PRINCIPAL ---
if st.session_state.radar:
    st.subheader("📋 Carteira sob Monitorização")
    cols = st.columns(len(st.session_state.radar))
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v440(t_at)
        if dat:
            p_now = dat['pa']
            lucro = ((p_now / cfg['p_in']) - 1) * 100
            with cols[i]:
                st.metric(t_at, f"R$ {p_now:,.2f}", f"{lucro:.2f}%")
                if st.button(f"Sair {t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

if st.session_state.consulta_fixa:
    d = analisar_v440(st.session_state.consulta_fixa)
    if d:
        st.subheader(f"🔍 Análise Profissional: {st.session_state.consulta_fixa}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{d['pa']:,.2f}")
        
        if d["tem_fundamentos"]:
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
            c3.metric("Dividend Yield", f"{d['div_a']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
        else:
            c2.metric("Suporte (LTA)", f"{d['sup_lta']:,.2f}")
            c3.metric("Resistência (LTB)", f"{d['res_ltb']:,.2f}")
            c4.metric("Div. Mensal", f"{d['div_m']:.3f}%")

        # Gráfico com Canais
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1), name="Média 20d"))
        fig.add_hline(y=d['sup_lta'], line_dash="dash", line_color="green", annotation_text="Suporte")
        fig.add_hline(y=d['res_ltb'], line_dash="dash", line_color="red", annotation_text="Resistência")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
