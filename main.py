import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface (Nexus Pro Layout)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; }
    .trader-box { background-color: #121212; color: #00FF00; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #00FF00; font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência Sincronizado (Fim da divergência MELK3)
@st.cache_data(ttl=30)
def analisar_v690(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # AJUSTE DEFINITIVO: Soma real dos dividendos de 12 meses para bater com simulador
        div_hist = tk.actions['Dividends'].last('1y')
        pago_total_ano = div_hist.sum() if not div_hist.empty else 0
        renda_media_mensal = pago_total_ano / 12
        
        # Perfil Trader por Volatilidade (day trade vs swing trade)
        vol = h['Close'].pct_change().std() * np.sqrt(252)
        perfil = "🚀 DAY TRADE" if vol > 0.45 else "📈 SWING TRADE"
        
        d = {
            "h": h, "ticker": t_up, "pa": h['Close'].iloc[-1], "is_c": is_c,
            "renda_m": renda_media_mensal, "perfil": perfil, 
            "dy": (pago_total_ano/h['Close'].iloc[-1]) if pago_total_ano > 0 else 0,
            "sup": h['Low'].tail(30).min(), "res": h['High'].tail(30).max(),
            "pj": np.sqrt(22.5 * info.get('forwardEps', 0) * info.get('bookValue', 0)) if not is_c else 0
        }
        return d
    except: return None

# --- MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR NEXUS COMMAND ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    meta_renda = st.number_input("Objetivo Renda Mensal (R$):", value=1000.0)
    with st.form("nexus_form", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, MELK3, JEPP34):").upper().strip()
        p_in = st.number_input("Preço de Entrada (R$ ou US$):", min_value=0.0)
        qtd = st.number_input("Quantidade Atual:", min_value=0)
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        if st.form_submit_button("🚀 Analisar Profissionalmente"):
            if t_in:
                st.session_state.radar[t_in] = {"p_in": p_in, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. MONITORAMENTO E EVOLUÇÃO (image_e19226.png)
if st.session_state.radar:
    st.subheader("📋 Gestão de Patrimônio")
    cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v690(t_at)
        if dat:
            evolucao = ((dat['pa'] / cfg['p_in']) - 1) * 100 if cfg['p_in'] > 0 else 0
            lucro_meta = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > cfg['p_in'] else 0
            
            with cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{evolucao:.2f}%")
                if lucro_meta > 0:
                    st.success(f"Lucro Alvo: R$ {lucro_meta:,.2f}")
                if st.button(f"Sair {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. SIMULADOR E TRADER (image_ef96df.jpg)
if st.session_state.consulta:
    d = analisar_v690(st.session_state.consulta)
    if d:
        st.divider()
        st.markdown(f"<div class='trader-box'>VEREDITO TRADER: {d['perfil']}</div>", unsafe_allow_html=True)
        
        # Sincronização MELK3 (image_f07760.png)
        if d['renda_m'] > 0:
            qtd_meta = int(meta_renda / d['renda_m'])
            investimento = qtd_meta * d['pa']
            c1, c2, c3 = st.columns(3)
            c1.metric("Capital Necessário", f"R$ {investimento:,.2f}")
            c2.metric("Ações Necessárias", f"{qtd_meta} un")
            c3.metric("Div. Yield Real", f"{d['dy']*100:.2f}%")
            st.info(f"💡 Planejamento: Invista R$ {investimento:,.2f} para renda de R$ {meta_renda:,.2f} em {d['ticker']}.")

        # Gráfico Master (image_e1ef81.png)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close, name="Preço")])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="COMPRA (LTA)")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="VENDA (LTB)")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
