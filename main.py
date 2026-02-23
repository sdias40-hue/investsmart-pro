import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium
st.set_page_config(page_title="Sandro Dividend Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Busca com Histórico de Proventos
@st.cache_data(ttl=60)
def analisar_v460(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="90d", interval="1d")
        if h.empty: return None
        
        # Captura de Dividendos (Histórico)
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        
        info = tk.info
        div_raw = info.get('dividendYield', 0) or info.get('yield', 0) or 0
        div_real = (div_raw * 100) if (div_raw < 1) else (div_raw / 100 if div_raw > 100 else div_raw)
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_m": div_real / 12, "div_a": div_real, "div_hist": div_hist,
            "setor": info.get('sector', 'BDR / ETF / Outros')
        }

        # Fundamentos e Blindagem
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        if lpa and vpa and not is_c and info.get('quoteType') == 'EQUITY':
            d["pj"] = np.sqrt(22.5 * lpa * vpa)
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["tem_fund"] = True
        else:
            d["pj"], d["roe"], d["tem_fund"] = 0, 0, False
        
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: GESTÃO ---
with st.sidebar:
    st.title("🛡️ Central Sandro Pro")
    with st.form("form_master", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3, METB34):").upper().strip()
        p_compra = st.number_input("Preço Entrada:", min_value=0.0, format="%.2f")
        alvo = st.number_input("Alvo de Venda:", min_value=0.0, format="%.2f")
        
        c1, c2 = st.columns(2)
        if c1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta = t_in; st.rerun()
        if c2.form_submit_button("📈 Monitorar"):
            if t_in and p_compra > 0:
                st.session_state.radar[t_in] = {"p_in": p_compra, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()

    if st.button("🧹 Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. CARDS DE MONITORAMENTO
if st.session_state.radar:
    st.subheader("📋 Carteira sob Vigilância")
    m_cols = st.columns(4)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v460(t_at)
        if dat:
            p_now = dat['pa']
            lucro = ((p_now / cfg['p_in']) - 1) * 100
            with m_cols[i % 4]:
                st.metric(t_at, f"R$ {p_now:,.2f}", f"{lucro:.2f}%")

# 2. ÁREA DE ANÁLISE DETALHADA
if st.session_state.consulta:
    d = analisar_v460(st.session_state.consulta)
    if d:
        st.divider()
        st.subheader(f"🔍 Análise Profissional: {st.session_state.consulta}")
        
        # Métricas Principais
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        if d["tem_fund"]:
            col2.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
            col3.metric("Div. Yield Anual", f"{d['div_a']:.2f}%")
            col4.metric("ROE", f"{d['roe']:.1f}%")
        else:
            col2.metric("Suporte (LTA)", f"R$ {d['sup']:,.2f}")
            col3.metric("Resistência (LTB)", f"R$ {d['res']:,.2f}")
            col4.metric("Div. Mensal Est.", f"{d['div_m']:.3f}%")

        # NOVA SECÇÃO: HISTÓRICO DE DIVIDENDOS
        if not d['div_hist'].empty:
            with st.expander("📅 Histórico de Pagamentos (Últimos 12 meses)", expanded=True):
                df_div = d['div_hist'].reset_index()
                df_div.columns = ['Data do Pagamento', 'Valor (R$)']
                df_div['Data do Pagamento'] = df_div['Data do Pagamento'].dt.strftime('%d/%m/%Y')
                st.table(df_div.sort_index(ascending=False))
        else:
            st.info("ℹ️ Sem histórico de dividendos em dinheiro nos últimos 12 meses para este ativo.")

        # Gráfico
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red")
        fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
