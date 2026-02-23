import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (Nexus Pro Layout)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    .trader-box { background-color: #121212; color: #00FF00; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #00FF00; font-size: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência Trader e Dividendos (Sincronização Total)
@st.cache_data(ttl=30)
def analisar_v670(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # AJUSTE DEFINITIVO DE DIVIDENDOS: Sincronizado com Analise de Ações (image_e4c01e.png)
        div_hist = tk.actions['Dividends'].last('1y')
        total_pago = div_hist.sum()
        renda_mensal_media = total_pago / 12
        dy_real = (total_pago / h['Close'].iloc[-1])

        # Inteligência Trader: Volatilidade e Tendência (image_ef96df.jpg)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        h['Vol'] = h['Close'].pct_change().std() * np.sqrt(252)
        perfil = "🚀 DAY TRADE (Foco Intraday)" if h['Vol'].iloc[-1] > 0.45 else "📈 SWING TRADE (Foco Tendência)"
        
        d = {
            "h": h, "ticker": t_up, "pa": h['Close'].iloc[-1], "is_c": is_c,
            "dy": dy_real, "perfil": perfil, "div_mensal": renda_mensal_media,
            "sup": h['Low'].tail(30).min(), "res": h['High'].tail(30).max()
        }
        return d
    except: return None

# --- MEMÓRIA NEXUS ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR NEXUS COMMAND ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    meta_renda = st.number_input("Objetivo Renda Mensal (R$):", value=1000.0)
    
    with st.form("nexus_form", clear_on_submit=True):
        t_in = st.text_input("Ticker:").upper().strip()
        p_in = st.number_input("Preço de Compra (R$):", min_value=0.0)
        qtd = st.number_input("Quantidade:", min_value=0)
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        if st.form_submit_button("🚀 Analisar Profissionalmente"):
            if t_in:
                st.session_state.radar[t_in] = {"p_in": p_in, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()
    
    if st.button("🗑️ Limpar Registro"):
        st.session_state.radar = {}; st.session_state.consulta = None; st.rerun()

# --- PAINEL PRINCIPAL ---
if st.session_state.radar:
    st.subheader("📋 Gestão de Patrimônio e Lucros")
    cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v670(t_at)
        if dat:
            evolucao = ((dat['pa'] / cfg['p_in']) - 1) * 100 if cfg['p_in'] > 0 else 0
            lucro_meta = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > cfg['p_in'] else 0
            
            with cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{evolucao:.2f}% (Evolução)")
                if lucro_meta > 0:
                    st.success(f"Lucro na Meta: R$ {lucro_meta:,.2f} (Alvo: {cfg['alvo']})")

if st.session_state.consulta:
    d = analisar_v670(st.session_state.consulta)
    if d:
        st.divider()
        # 1. PERFIL TRADER MASTER (image_d69d3b.jpg)
        st.markdown(f"<div class='trader-box'>ESTRATÉGIA MASTER: {d['perfil']}</div>", unsafe_allow_html=True)
        
        # 2. SIMULADOR DE INVESTIMENTO (Bate com Analise de Ações image_e439b3.png)
        if d['div_mensal'] > 0:
            qtd_meta = int(meta_renda / d['div_mensal'])
            investimento = qtd_meta * d['pa']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Capital para R$ 1.000", f"R$ {investimento:,.2f}")
            c2.metric("Ações Necessárias", f"{qtd_meta} un")
            c3.metric("Dividend Yield Real", f"{d['dy']*100:.2f}%")
            st.info(f"💡 Planejamento: Invista R$ {investimento:,.2f} em {d['ticker']} para renda mensal de R$ {meta_renda:,.2f}")

        # 3. GRÁFICO TRADER (Estilo image_ef96df.jpg)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close, name="Preço")])
        
        # Linhas de Tendência e Sinais (Comp/Vend)
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="LTA - COMPRA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="LTB - VENDA")
        
        fig.update_layout(height=500, template='plotly_white', xaxis_rangeslider_visible=False, title=f"Análise de Tendência e Sinais: {d['ticker']}")
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
