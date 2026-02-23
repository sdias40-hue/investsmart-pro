import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface (Layout Nexus Pro)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    .trader-box { background-color: #1E1E1E; color: #00FF00; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Precisão Trader e Dividendos (Correção MELK3)
@st.cache_data(ttl=30)
def analisar_v660(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # AJUSTE DE PRECISÃO: Sincronizando DY com Investidor10 para bater R$ 25k na MELK3
        dy_anual = info.get('dividendYield', 0)
        if dy_anual > 0.5: dy_anual = dy_anual / 100 # Corrige escala se vier errada
        
        # Inteligência Trader: Volatilidade Real
        vol = h['Close'].pct_change().std() * np.sqrt(252)
        perfil = "🚀 DAY TRADE" if vol > 0.40 else "📈 SWING TRADE"

        d = {
            "h": h, "ticker": t_up, "pa": h['Close'].iloc[-1], "is_c": is_c,
            "dy": dy_anual, "perfil": perfil, "vol": vol,
            "setor": info.get('sector', 'N/A'), "roe": (info.get('returnOnEquity', 0) or 0) * 100,
            "sup": h['Low'].tail(30).min(), "res": h['High'].tail(30).max()
        }
        return d
    except: return None

# --- MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR NEXUS ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    obj_renda = st.number_input("Meta Renda Mensal (R$):", value=1000.0)
    
    with st.form("nexus_form", clear_on_submit=True):
        t_in = st.text_input("Ticker:").upper().strip()
        p_in = st.number_input("Preço de Compra (R$):", min_value=0.0)
        qtd = st.number_input("Quantidade:", min_value=0)
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        if st.form_submit_button("🚀 Executar"):
            if t_in:
                st.session_state.radar[t_in] = {"p_in": p_in, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()
    
    if st.button("🗑️ Limpar Registro"):
        st.session_state.radar = {}; st.session_state.consulta = None; st.rerun()

# --- PAINEL PRINCIPAL ---
if st.session_state.radar:
    st.subheader("📋 Evolução e Alvos")
    cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v660(t_at)
        if dat:
            # Lucro/Prejuízo Atual
            evolucao = ((dat['pa'] / cfg['p_in']) - 1) * 100 if cfg['p_in'] > 0 else 0
            # Lucro na Meta e IR (15%)
            lucro_bruto = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > cfg['p_in'] else 0
            ir_estimado = lucro_bruto * 0.15 if lucro_bruto > 0 else 0
            
            with cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{evolucao:.2f}% (Evolução)")
                if lucro_bruto > 0:
                    st.success(f"Lucro Alvo: R$ {lucro_bruto:,.2f}")
                    st.warning(f"Estimativa IR: R$ {ir_estimado:,.2f}")

if st.session_state.consulta:
    d = analisar_v660(st.session_state.consulta)
    if d:
        st.divider()
        # 1. PERFIL TRADER (Destaque visual novo)
        st.markdown(f"<div class='trader-box'>PERFIL SUGERIDO: {d['perfil']}</div>", unsafe_allow_html=True)
        
        # 2. SIMULADOR DE RENDA (Sincronizado com Mercado)
        if d['dy'] > 0:
            inv_total = (obj_renda * 12) / d['dy']
            q_acoes = inv_total / d['pa']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Capital p/ Meta", f"R$ {inv_total:,.2f}")
            c2.metric("Ações Necessárias", f"{int(q_acoes)} un")
            c3.metric("Div. Yield Real", f"{d['dy']*100:.2f}%")
            st.info(f"💡 Para renda de R$ {obj_renda:,.2f}, o capital necessário é R$ {inv_total:,.2f} em {d['ticker']}.")

        # 3. MÉTRICAS E GRÁFICO LTA/LTB
        m1, m2, m3 = st.columns(3)
        m1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        m2.metric("Suporte (LTA)", f"R$ {d['sup']:,.2f}")
        m3.metric("Resistência (LTB)", f"R$ {d['res']:,.2f}")

        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="LTA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="LTB")
        fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
