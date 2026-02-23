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

# 2. Motor de Análise e Dividendos Sincronizado
@st.cache_data(ttl=60)
def analisar_v600(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        total_pago_12m = div_hist.sum()
        
        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_12m": total_pago_12m, "freq": "Mensal" if len(div_hist) >= 10 else "Anual/Semestral",
            "setor": info.get('sector', 'N/A'), "div_hist": div_hist
        }

        # Fundamentos Graham
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Canais Técnicos (LTA/LTB)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: GESTÃO DE INVESTIMENTOS ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    obj_renda = st.number_input("Meta Renda Mensal (R$):", min_value=0.0, value=1000.0)
    
    with st.form("form_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3, GRND3):").upper().strip()
        p_avg = st.number_input("Preço Médio (R$):", min_value=0.0, format="%.2f")
        qtd = st.number_input("Quantidade:", min_value=0, step=1)
        p_alvo = st.number_input("Preço Alvo Venda (R$):", min_value=0.0, format="%.2f")
        
        c1, c2 = st.columns(2)
        if c1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta = t_in; st.rerun()
        if c2.form_submit_button("📈 Monitorar"):
            if t_in and p_avg > 0:
                st.session_state.radar[t_in] = {"p_in": p_avg, "qtd": qtd, "alvo": p_alvo}
                st.session_state.consulta = t_in; st.rerun()

    if st.button("🗑️ Limpar Registro"):
        st.session_state.radar, st.session_state.consulta = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. MONITORAMENTO (Com Lucro Alvo Real)
if st.session_state.radar:
    st.subheader("📋 Patrimônio sob Monitoramento")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v600(t_at)
        if dat:
            lucro_atual_pct = ((dat['pa'] / cfg['p_in']) - 1) * 100
            # LUCRO ESTIMADO SE ATINGIR O ALVO
            lucro_na_meta = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > cfg['p_in'] else 0
            
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{lucro_atual_pct:.2f}%")
                if lucro_na_meta > 0:
                    st.success(f"💰 Lucro na Meta: R$ {lucro_na_meta:,.2f}")
                    st.caption(f"Alvo: R$ {cfg['alvo']:.2f}")
                if st.button(f"Remover {t_at}", key=f"del_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. CONSULTA, MENTOR E SIMULADOR DE CAPITAL
if st.session_state.consulta:
    d = analisar_v600(st.session_state.consulta)
    if d:
        st.divider()
        st.subheader(f"🔍 Nexus Intelligence: {st.session_state.consulta}")
        
        # SIMULADOR DE INVESTIMENTO PARA RENDA (Meta R$ 1000)
        if not d['is_c'] and d['div_12m'] > 0:
            div_mensal_estimado = d['div_12m'] / 12
            qtd_necessaria = int(obj_renda / div_mensal_estimado)
            investimento_necessario = qtd_necessaria * d['pa']
            
            s1, s2, s3 = st.columns(3)
            with s1: st.metric("Quantidade p/ Meta", f"{qtd_necessaria} ações")
            with s2: st.metric("Capital Necessário", f"R$ {investimento_necessario:,.2f}")
            with s3: st.metric("Renda Mensal Alvo", f"R$ {obj_renda:,.2f}")
            st.info(f"💡 Para receber R$ {obj_renda:,.2f} mensais de {d['ticker']}, você precisa investir aproximadamente R$ {investimento_necessario:,.2f}.")

        # MÉTRICAS TÉCNICAS E GRÁFICO
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Preço Justo (Graham)", f"R$ {d['pj']:,.2f}")
        c3.metric("Div. 12m Acumulado", f"R$ {d['div_12m']:,.2f}")
        c4.metric("Periodicidade", d['freq'])

        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte LTA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência LTB")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
