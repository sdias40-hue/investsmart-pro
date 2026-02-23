import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência Sincronizado (Correção GRND3)
@st.cache_data(ttl=60)
def analisar_v580(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        # Sincronização de Proventos Reais (image_e2eea1.png)
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        total_pago_12m = div_hist.sum()
        
        # Cálculo de Periodicidade Real (image_e2eea1.png)
        freq = "Irregular"
        if not div_hist.empty:
            count = len(div_hist)
            if count >= 10: freq = "Mensal"
            elif 2 <= count <= 4: freq = "Semestral"
            else: freq = "Anual"

        d = {
            "h": h, "info": tk.info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_12m": total_pago_12m, "freq": freq, "div_hist": div_hist,
            "dy": (total_pago_12m / h['Close'].iloc[-1]) * 100 if total_pago_12m > 0 else 0
        }
        
        # Canais Técnicos (image_e2d41e.png)
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA ---
if 'carteira' not in st.session_state: st.session_state.carteira = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: GESTÃO E ALVO DE RENDA ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    renda_objetivo = st.number_input("Objetivo de Renda Mensal (R$):", min_value=0.0, value=1000.0)
    
    with st.form("comando_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, GRND3):").upper().strip()
        p_avg = st.number_input("Preço de Compra (R$):", min_value=0.0)
        qtd = st.number_input("Quantidade:", min_value=0, step=1)
        
        if st.form_submit_button("📈 Monitorar e Simular"):
            if t_in:
                st.session_state.carteira[t_in] = {"p_avg": p_avg, "qtd": qtd}
                st.session_state.consulta = t_in; st.rerun()

    if st.button("🗑️ Limpar Monitoramento"):
        st.session_state.carteira = {}; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. SIMULADOR DE LIBERDADE FINANCEIRA (NOVO!)
if st.session_state.consulta:
    d = analisar_v580(st.session_state.consulta)
    if d and d['div_12m'] > 0:
        st.subheader(f"🚀 Simulador de Renda: {d['ticker']}")
        # Cálculo: Renda Mensal Desejada / (Total Pago no Ano / 12 meses)
        div_mensal_medio = d['div_12m'] / 12
        acoes_necessarias = int(renda_objetivo / div_mensal_medio)
        investimento_total = acoes_necessarias * d['pa']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Ações Necessárias", f"{acoes_necessarias} un")
        c2.metric("Investimento Total", f"R$ {investimento_total:,.2f}")
        c3.metric("Renda Mensal Estimada", f"R$ {renda_objetivo:,.2f}")
        st.caption(f"Baseado no pagamento de R$ {d['div_12m']:.2f}/ação nos últimos 12 meses. [Cotação: R$ {d['pa']:.2f}]")
        st.divider()

# 2. CARTEIRA E LIMPEZA INDIVIDUAL (image_e2d41e.png)
if st.session_state.carteira:
    st.subheader("📋 Monitoramento e Renda Atual")
    m_cols = st.columns(len(st.session_state.carteira))
    for i, (t_at, cfg) in enumerate(st.session_state.carteira.items()):
        dat = analisar_v580(t_at)
        if dat:
            renda_anual = dat['div_12m'] * cfg['qtd']
            with m_cols[i]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"Anual: R$ {renda_anual:,.2f}")
                if st.button(f"Sair {t_at}", key=f"rm_{t_at}"):
                    del st.session_state.carteira[t_at]; st.rerun()

time.sleep(30)
st.rerun()
