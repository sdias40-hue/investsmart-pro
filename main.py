import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (image_d4d43a.png)
st.set_config(page_title="Sandro Planning Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Análise com Planejamento de Proventos
@st.cache_data(ttl=60)
def analisar_v550(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d") # 1 ano para bater com Investidor10
        if h.empty: return None
        
        info = tk.info
        # Sincronização de Dividendos com Investidor10 (image_e20629.png)
        div_hist = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        dy_calculado = (div_hist.sum() / h['Close'].iloc[-1]) * 100 if not div_hist.empty else 0
        
        # Identificação de Periodicidade (image_e1f6e1.jpg)
        frequencia = "Irregular"
        if not div_hist.empty:
            contagem = len(div_hist)
            if contagem >= 10: frequencia = "Mensal"
            elif 3 <= contagem <= 5: frequencia = "Trimestral"
            elif contagem == 2: frequencia = "Semestral"
            elif contagem == 1: frequencia = "Anual"

        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "dy": dy_calculado, "freq": frequencia, "div_total": div_hist.sum(),
            "setor": info.get('sector', 'N/A'), "div_hist": div_hist
        }

        # Fundamentos (Preço Justo Graham - image_e20607.png)
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
        
        # Canais Técnicos (image_4c07e0.png)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- MEMÓRIA SANDRO ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_fixa' not in st.session_state: st.session_state.consulta_fixa = None

# --- SIDEBAR: GESTÃO ---
with st.sidebar:
    st.title("🛡️ Central Sandro Pro")
    with st.form("form_master", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, PETR4, BTC):").upper().strip()
        p_compra = st.number_input("Preço Entrada (R$):", min_value=0.0, format="%.2f")
        alvo = st.number_input("Alvo de Venda:", min_value=0.0, format="%.2f")
        
        c1, c2 = st.columns(2)
        if c1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta_fixa = t_in; st.rerun()
        if c2.form_submit_button("📈 Monitorar"):
            if t_in and p_compra > 0:
                st.session_state.radar[t_in] = {"p_in": p_compra, "alvo": alvo}
                st.session_state.consulta_fixa = t_in; st.rerun()

# --- PAINEL PRINCIPAL ---
if st.session_state.radar:
    st.subheader("📋 Monitoramento Ativo")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v550(t_at)
        if dat:
            lucro = ((dat['pa'] / cfg['p_in']) - 1) * 100
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{lucro:.2f}%")

if st.session_state.consulta_fixa:
    d = analisar_v550(st.session_state.consulta_fixa)
    if d:
        st.divider()
        st.subheader(f"🔍 Planejamento Financeiro: {st.session_state.consulta_fixa}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Preço Justo (Graham)", f"R$ {d['pj']:,.2f}")
        c3.metric("Dividend Yield (12m)", f"{d['dy']:.2f}%")
        c4.metric("Periodicidade", d['freq'])
        
        # MENSAGEM DO MENTOR (image_4b1f9e.jpg)
        st.info(f"📅 **Mentor Planejamento:** O ativo {d['ticker']} tem pagamento **{d['freq']}**. "
                f"No último ano, pagou um total de R$ {d['div_total']:.2f} por cota.")

        # Histórico de Dividendos e Gráfico
        with st.expander("📊 Detalhes de Proventos e Tendência", expanded=True):
            col_g1, col_g2 = st.columns([1, 2])
            with col_g1:
                if not d["div_hist"].empty:
                    st.write("**Pagamentos Recebidos (12m):**")
                    st.table(d["div_hist"].reset_index().rename(columns={'Date':'Data','Dividends':'Valor R$'}))
            with col_g2:
                fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
                fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte")
                fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
