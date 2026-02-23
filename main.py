import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (Recuperando image_d4d43a.png)
st.set_page_config(page_title="Sandro Master Cloud", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência e Especialidade Trader
@st.cache_data(ttl=60)
def analisar_v530(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # Correção Escala Dividendos (image_4b1f9e.jpg)
        div_raw = info.get('dividendYield', 0) or info.get('yield', 0) or 0
        div_f = (div_raw * 100) if (div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_a": div_f, "setor": info.get('sector', 'Trader Assets')
        }

        # Especialidade Trader (image_d69d3b.jpg)
        h['Vol'] = h['Close'].pct_change().std() * np.sqrt(252)
        d["perfil"] = "Day Trader" if h['Vol'].iloc[-1] > 0.45 else "Swing Trader"
        
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        if lpa and vpa and not is_c and info.get('quoteType') == 'EQUITY':
            d["pj"] = np.sqrt(22.5 * lpa * vpa)
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["tem_fund"] = True
        else:
            d["pj"], d["roe"], d["tem_fund"] = 0, 0, False
        
        # Tendências Técnicas (image_4c07e0.png)
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: GESTÃO SANDRO (Limpeza Corrigida) ---
with st.sidebar:
    st.title("🛡️ Central Sandro Pro")
    with st.form("form_v530", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço de Compra:", min_value=0.0, format="%.2f")
        qtd = st.number_input("Quantidade:", min_value=0, step=1)
        alvo = st.number_input("Preço de Venda (Alvo):", min_value=0.0, format="%.2f")
        
        c1, c2 = st.columns(2)
        if c1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta = t_in; st.rerun()
        if c2.form_submit_button("📈 Monitorar"):
            if t_in and p_ent > 0:
                st.session_state.radar[t_in] = {"p_in": p_ent, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()

    if st.button("🧹 Limpar Registro"):
        st.session_state.radar, st.session_state.consulta = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. MONITORAMENTO (Cards com Lucro Projetado image_d70dc2.png)
if st.session_state.radar:
    st.subheader("📋 Monitoramento Ativo")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v530(t_at)
        if dat:
            p_now = dat['pa']
            lucro_atual = ((p_now / cfg['p_in']) - 1) * 100
            # CORREÇÃO DA LINHA 89: Lucro Projetado
            lucro_est = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > cfg['p_in'] else 0
            
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {p_now:,.2f}", f"{lucro_atual:.2f}%")
                st.caption(f"🎯 Alvo: R$ {cfg['alvo']:,.2f} | 💰 Lucro Projetado: R$ {lucro_est:,.2f}")
                if st.button(f"Sair {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. ANÁLISE DE TRADER (Opinião do Mentor e BTC)
if st.session_state.consulta:
    d = analisar_v530(st.session_state.consulta)
    if d:
        st.divider()
        st.subheader(f"🔍 Perfil Trader Master: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Perfil Sugerido", d["perfil"])
        
        if d["tem_fund"]:
            c3.metric("Dividendos", f"{d['div_a']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            st.success(f"✅ **Veredito:** Ativo de {d['setor']} ideal para **{d['perfil']}**. Fundamentos sólidos.")
        else:
            c3.metric("Suporte (LTA)", f"R$ {d['sup']:,.2f}")
            c4.metric("Resistência (LTB)", f"R$ {d['res']:,.2f}")
            # Alerta técnico para BTC (image_4c07e0.png)
            if d['ticker'] == 'BTC':
                dist = ((d['pa'] / d['sup']) - 1) * 100
                if dist < 3: st.info("🔥 **Oportunidade de Compra:** BTC tocando o suporte. Ótimo para Swing Trade!")

        # Gráfico Profissional (Linhas de Tendência)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
