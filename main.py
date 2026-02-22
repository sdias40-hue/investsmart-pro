import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface (Resolução image_41cf82.png)
st.set_page_config(page_title="Sandro Cloud Pro", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise com Canais de Tendência e Blindagem
@st.cache_data(ttl=60)
def analisar_v430(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # Correção Escala Dividendo (image_4b1f9e.jpg)
        div_anual = info.get('dividendYield', 0) or info.get('yield', 0) or 0
        div_real = (div_anual * 100) if (div_anual < 1) else (div_anual / 100 if div_anual > 100 else div_anual)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_m": div_real / 12, "div_s": div_real / 2, "div_a": div_real,
            "setor": info.get('sector', 'N/A'), "roe": (info.get('returnOnEquity', 0) or 0) * 100
        }

        # Blindagem JEPP34: Evita cálculo de Graham em ativos sem balanço
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Canais de Tendência (LTA/LTB) - image_4c07e0.png
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup_lta"] = h['Low'].tail(30).min()
        d["res_ltb"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA SANDRO ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_fixa' not in st.session_state: st.session_state.consulta_fixa = None

# --- SIDEBAR: GESTÃO DE CARTEIRA ---
with st.sidebar:
    st.title("🛡️ Sandro Cloud Pro")
    with st.form("comando_master", clear_on_submit=False):
        t_in = st.text_input("Ticker:", value=st.session_state.consulta_fixa or "").upper().strip()
        
        # Layout Dinâmico: R$ para Cripto, Qtd para Ações
        is_c_check = t_in in ["BTC", "ETH", "SOL", "XRP"]
        if is_c_check:
            val_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            p_compra = st.number_input("Preço de Entrada (US$):", min_value=0.0)
        else:
            p_compra = st.number_input("Preço de Compra (R$):", min_value=0.0)
            qtd = st.number_input("Quantidade de Ações:", min_value=0, step=1)
        
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        col_b1, col_b2 = st.columns(2)
        if col_b1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta_fixa = t_in; st.rerun()
        if col_b2.form_submit_button("📈 Monitorar"):
            if t_in and p_compra > 0:
                st.session_state.radar[t_in] = {"p_in": p_compra, "alvo": alvo, "is_c": is_c_check}
                st.session_state.consulta_fixa = t_in; st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal Sandro Master | Gestão 24h")

# 1. MONITORAMENTO ATIVO (Fixado no topo)
if st.session_state.radar:
    st.subheader("📋 Monitoramento de Carteira")
    for t_at, cfg in list(st.session_state.radar.items()):
        dat = analisar_v430(t_at)
        if dat:
            p_now = dat['pa']
            lucro = ((p_now / cfg['p_in']) - 1) * 100
            with st.expander(f"📈 {t_at} | R$ {p_now:,.2f} ({lucro:.2f}%)", expanded=True):
                c_m1, c_m2, c_m3 = st.columns(3)
                c_m1.metric("Alvo", f"{cfg['alvo']:,.2f}")
                c_m2.metric("Suporte (LTA)", f"{dat['sup_lta']:,.2f}")
                if c_m3.button(f"Remover {t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. CONSULTA (LTA/LTB e Mentor Sandro)
if st.session_state.consulta_fixa:
    d = analisar_v430(st.session_state.consulta_fixa)
    if d:
        st.subheader(f"🔍 Análise de Tendência: {st.session_state.consulta_fixa}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{d['pa']:,.2f}")
        
        if not d['is_c'] and d['pj'] > 0:
            c2.metric("Preço Justo (Graham)", f"R$ {d['pj']:,.2f}")
            c3.metric("Div. Mensal", f"{d['div_m']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            st.info(f"✅ **Mentor Sandro:** Ativo de {d['setor']}. Tendência de ALTA acima da Média 20d.")
        else:
            c2.metric("Suporte (LTA)", f"{d['sup_lta']:,.2f}")
            c3.metric("Resistência (LTB)", f"{d['res_ltb']:,.2f}")
            st.warning("🤖 **Mentor:** Ativo em análise técnica. Foco nos rompimentos de canal.")

        # Gráfico Profissional (Canais e Médias)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1), name="Média 20d"))
        fig.add_hline(y=d['sup_lta'], line_dash="dash", line_color="green", annotation_text="LTA")
        fig.add_hline(y=d['res_ltb'], line_dash="dash", line_color="red", annotation_text="LTB")
        fig.update_layout(height=500, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
