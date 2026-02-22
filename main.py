import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface (Resolução image_41cf82.png)
st.set_page_config(page_title="Sandro Master Analyst", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise com Tendências (LTA/LTB) e Blindagem (JEPP34)
@st.cache_data(ttl=60)
def analisar_v420(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # Correção Escala Dividendo (image_4b1f9e.jpg)
        div_raw = info.get('dividendYield', 0) or info.get('yield', 0) or 0
        div_f = (div_raw * 100) if (div_raw and div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div": div_f, "setor": info.get('sector', 'N/A'), "roe": (info.get('returnOnEquity', 0) or 0) * 100
        }

        # Evita erro JEPP34/RILYT ao pular Graham se não houver dados (image_42397b.png)
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Cálculo de Tendências (image_4b1f9e.jpg)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA SANDRO ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_ativa' not in st.session_state: st.session_state.consulta_ativa = None

# --- SIDEBAR: CONSULTA E MONITORAMENTO ---
with st.sidebar:
    st.title("🛡️ Sandro Cloud Pro")
    with st.form("comando_sandro", clear_on_submit=False):
        t_in = st.text_input("Ticker (VULC3, JEPP34, BTC):", value=st.session_state.consulta_ativa or "").upper().strip()
        p_compra = st.number_input("Preço de Compra (Para Monitorar):", min_value=0.0, format="%.2f")
        qtd = st.number_input("Quantidade:", min_value=0, step=1)
        alvo = st.number_input("Alvo de Venda:", min_value=0.0, format="%.2f")
        
        c_cols = st.columns(2)
        if c_cols[0].form_submit_button("🔍 Consultar"):
            if t_in:
                st.session_state.consulta_ativa = t_in
                st.rerun()
        
        if c_cols[1].form_submit_button("📈 Monitorar"):
            if t_in and p_compra > 0:
                st.session_state.radar[t_in] = {"p_in": p_compra, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta_ativa = t_in
                st.rerun()

    if st.button("🧹 Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta_ativa = {}, None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal Sandro Master | Análise & Tendência")

# 1. MONITORAMENTO (Fixado no Topo)
if st.session_state.radar:
    st.subheader("📋 Monitoramento de Carteira")
    for t_at, cfg in list(st.session_state.radar.items()):
        dat = analisar_v420(t_at)
        if dat:
            p_now = dat['pa']
            lucro_pct = ((p_now / cfg['p_in']) - 1) * 100
            lucro_brl = (p_now - cfg['p_in']) * cfg['qtd']
            with st.expander(f"📈 {t_at} | R$ {p_now:,.2f} ({lucro_pct:.2f}%)", expanded=True):
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Lucro R$", f"R$ {lucro_brl:,.2f}")
                col_m2.metric("Alvo", f"R$ {cfg['alvo']:,.2f}")
                if col_m3.button(f"Remover {t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
                if cfg['alvo'] > 0 and p_now >= cfg['alvo']:
                    st.error(f"🎯 ALVO ATINGIDO EM {t_at}!")

# 2. CONSULTA DETALHADA (LTA/LTB e Mentor)
if st.session_state.consulta_ativa:
    d = analisar_v420(st.session_state.consulta_ativa)
    if d:
        st.subheader(f"🔍 Análise de Tendência: {st.session_state.consulta_ativa}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"{d['pa']:,.2f}")
        
        if not d['is_c'] and d['pj'] > 0:
            upside = ((d['pj']/d['pa'])-1)*100
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("Div. Yield", f"{d['div']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            
            # MENTOR DETALHADO (Recuperado)
            tendencia = "ALTA" if d['pa'] > d['h']['MA20'].iloc[-1] else "BAIXA"
            msg = f"✅ **Mentor Sandro:** Ativo de {d['setor']} com ROE de {d['roe']:.1f}%. "
            msg += f"Tendência de {tendencia} acima da Média de 20 dias. "
            if d['pa'] <= d['sup'] * 1.02: msg += "🔥 Ponto de compra por Pullback na LTA!"
            st.info(msg)
        else:
            c2.metric("Suporte (LTA)", f"{d['sup']:,.2f}")
            c3.metric("Resistência (LTB)", f"{d['res']:,.2f}")
            st.warning("🤖 **Mentor:** Ativo de Renda Fixa ou Cripto. Foco em suporte e resistência.")

        # Gráfico com Linhas de Tendência (image_4b1f9e.jpg)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1), name="Média 20d"))
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte / LTA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência / LTB")
        fig.update_layout(height=500, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
