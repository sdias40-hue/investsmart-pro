import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Interface Premium Blindada (image_d4d43a.png)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; }
    .trader-box { background-color: #121212; color: #00FF00; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #00FF00; font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Precisão Sincronizado (Fim do looping MELK3)
@st.cache_data(ttl=30)
def analisar_v700(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # AJUSTE MATEMÁTICO: Soma real 12 meses (image_f07760.png)
        div_hist = tk.actions['Dividends'].last('1y')
        pago_total_ano = div_hist.sum() if not div_hist.empty else 0
        renda_mensal_real = pago_total_ano / 12
        
        # Especialidade Trader (Day vs Swing - image_d69d3b.jpg)
        vol = h['Close'].pct_change().std() * np.sqrt(252)
        perfil = "🚀 DAY TRADE" if vol > 0.45 else "📈 SWING TRADE"
        
        d = {
            "h": h, "ticker": t_up, "pa": h['Close'].iloc[-1], "is_c": is_c,
            "renda_m": renda_mensal_real, "perfil": perfil, 
            "dy": (pago_total_ano/h['Close'].iloc[-1]) if pago_total_ano > 0 else 0,
            "sup": h['Low'].tail(30).min(), "res": h['High'].tail(30).max()
        }
        return d
    except: return None

# --- MEMÓRIA DO TERMINAL ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR NEXUS ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    obj_renda = st.number_input("Meta Renda Mensal (R$):", value=1000.0)
    with st.form("nexus_form", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, MELK3, BTC):").upper().strip()
        p_in = st.number_input("Preço Compra (R$ ou US$):", min_value=0.0)
        qtd = st.number_input("Quantidade:", min_value=0)
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        if st.form_submit_button("🚀 Analisar e Monitorar"):
            if t_in:
                st.session_state.radar[t_in] = {"p_in": p_in, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()
    if st.button("🗑️ Limpar Registro"):
        st.session_state.radar, st.session_state.consulta = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. MONITORAMENTO COM IMPOSTO DE RENDA (image_e4c47d.png)
if st.session_state.radar:
    st.subheader("📋 Gestão de Patrimônio")
    cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v700(t_at)
        if dat:
            evolucao = ((dat['pa'] / cfg['p_in']) - 1) * 100 if cfg['p_in'] > 0 else 0
            lucro_meta = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > cfg['p_in'] else 0
            ir_estimado = lucro_meta * 0.15 if lucro_meta > 0 else 0
            
            with cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{evolucao:.2f}%")
                if lucro_meta > 0:
                    st.success(f"Lucro Alvo Líquido: R$ {(lucro_meta - ir_estimado):,.2f}")
                if st.button(f"Sair {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. SIMULADOR E TRADER (image_ef96df.jpg)
if st.session_state.consulta:
    d = analisar_v700(st.session_state.consulta)
    if d:
        st.divider()
        st.markdown(f"<div class='trader-box'>VEREDITO TRADER: {d['perfil']}</div>", unsafe_allow_html=True)
        
        # Sincronização MELK3 (image_f07760.png)
        if d['renda_m'] > 0:
            qtd_meta = int(obj_renda / d['renda_m'])
            investimento = qtd_meta * d['pa']
            c1, c2, c3 = st.columns(3)
            c1.metric("Capital Necessário", f"R$ {investimento:,.2f}")
            c2.metric("Ações Necessárias", f"{qtd_meta} un")
            c3.metric("Dividend Yield (12m)", f"{d['dy']*100:.2f}%")

        # Gráfico Master LTA/LTB (image_e1ef81.png)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close, name="Preço")])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="COMPRA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="VENDA")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
