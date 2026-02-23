import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface (Layout Consolidado)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Inteligência e Proventos (Sincronizado)
@st.cache_data(ttl=60)
def analisar_v570(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        # Dados de Proventos Reais (image_e26b5e.png)
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        total_pago_12m = div_hist.sum()
        dy_real = (total_pago_12m / h['Close'].iloc[-1]) * 100 if not div_hist.empty else 0
        
        # Frequência e Previsão (image_e1f6e1.jpg)
        freq_msg = "Irregular"
        if not div_hist.empty:
            count = len(div_hist)
            if count >= 10: freq_msg = "Mensal"
            elif 2 <= count <= 4: freq_msg = "Semestral/Trimestral"
            else: freq_msg = "Anual"

        d = {
            "h": h, "info": tk.info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "dy": dy_real, "freq": freq_msg, "div_hist": div_hist, "total_12m": total_pago_12m,
            "ult_div": div_hist.iloc[-1] if not div_hist.empty else 0
        }

        # Fundamentos Graham (image_e20607.png)
        lpa, vpa = tk.info.get('forwardEps'), tk.info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Canais LTA/LTB (image_4c07e0.png)
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA DA CARTEIRA ---
if 'carteira' not in st.session_state: st.session_state.carteira = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: GESTÃO DE APORTES (image_4ba281.png) ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    with st.form("comando_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        p_avg = st.number_input("Preço Médio / Compra (R$):", min_value=0.0)
        qtd = st.number_input("Quantidade Atual:", min_value=0, step=1)
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        c1, c2 = st.columns(2)
        if c1.form_submit_button("🔍 Consultar"):
            st.session_state.consulta = t_in; st.rerun()
        if c2.form_submit_button("📈 Monitorar"):
            if t_in and qtd > 0:
                st.session_state.carteira[t_in] = {"p_avg": p_avg, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. CALCULADORA DE RENDA PASSIVA (NOVO!)
if st.session_state.carteira:
    st.subheader("💰 Planejador de Renda Nexus")
    m_cols = st.columns(len(st.session_state.carteira))
    total_renda_estimada = 0
    
    for i, (t_at, cfg) in enumerate(st.session_state.carteira.items()):
        dat = analisar_v570(t_at)
        if dat:
            # Previsão baseada no último pagamento
            renda_acao = dat['ult_div'] * cfg['qtd']
            total_renda_estimada += renda_acao
            with m_cols[i]:
                st.metric(f"{t_at} ({cfg['qtd']} un)", f"R$ {dat['pa']:,.2f}", f"Renda: R$ {renda_acao:,.2f}")
                st.caption(f"Freq: {dat['freq']} | Alvo: R$ {cfg['alvo']}")

# 2. ANÁLISE TÉCNICA E TENDÊNCIA
if st.session_state.consulta:
    d = analisar_v570(st.session_state.consulta)
    if d:
        st.divider()
        st.subheader(f"🔍 Nexus Intelligence: {st.session_state.consulta}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
        c3.metric("Dividend Yield", f"{d['dy']:.2f}%")
        c4.metric("Periodicidade", d['freq'])
        
        # Histórico e Gráfico (image_e26b5e.png)
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            st.write("**Histórico de Pagamentos:**")
            if not d["div_hist"].empty:
                st.table(d["div_hist"].reset_index().rename(columns={'Date':'Data','Dividends':'Valor R$'}))
        with col_g2:
            fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
            fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="LTA")
            fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="LTB")
            fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
