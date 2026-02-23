import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (Recuperando image_d4d43a.png)
st.set_page_config(page_title="Sandro Analyst Elite", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Análise Blindado e Inteligente
@st.cache_data(ttl=60)
def analisar_v480(t):
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
            "div_a": div_f, "div_m": div_f / 12, "setor": info.get('sector', 'BDR / ETF / Outros')
        }

        # Blindagem: Só calcula fundamentos se os dados existirem (image_42397b.png)
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        if lpa and vpa and not is_c and info.get('quoteType') == 'EQUITY':
            d["pj"] = np.sqrt(22.5 * lpa * vpa)
            d["roe"] = (info.get('returnOnEquity', 0) or 0) * 100
            d["tem_fund"] = True
        else:
            d["pj"], d["roe"], d["tem_fund"] = 0, 0, False
        
        # Tendências Técnicas (image_4c07e0.png)
        h['MA20'] = h['Close'].rolling(window=20).mean()
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        d["div_hist"] = tk.actions['Dividends'].last('1y') if not tk.actions.empty else pd.Series()
        
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_fixa' not in st.session_state: st.session_state.consulta_fixa = None

# --- SIDEBAR: GESTÃO SANDRO (Limpando registro image_d54c3d.png) ---
with st.sidebar:
    st.title("🛡️ Central Sandro Pro")
    with st.form("comando_master", clear_on_submit=True): # clear_on_submit resolve a limpeza
        t_in = st.text_input("Ticker (VULC3, RILYT, BTC):").upper().strip()
        is_cripto = t_in in ["BTC", "ETH", "SOL", "XRP"]
        
        p_compra = st.number_input("Preço Compra (R$ ou US$):", min_value=0.0, format="%.2f")
        if is_cripto:
            val_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
        else:
            qtd = st.number_input("Quantidade:", min_value=0, step=1)
            
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        col_b1, col_b2 = st.columns(2)
        if col_b1.form_submit_button("🔍 Consultar"):
            if t_in: st.session_state.consulta_fixa = t_in; st.rerun()
        if col_b2.form_submit_button("📈 Monitorar"):
            if t_in and p_compra > 0:
                st.session_state.radar[t_in] = {"p_in": p_compra, "alvo": alvo}
                st.session_state.consulta_fixa = t_in; st.rerun()

    if st.button("🧹 Limpar Tudo"):
        st.session_state.radar, st.session_state.consulta_fixa = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. CARDS DE MONITORAMENTO (Recuperando image_d4d43a.png)
if st.session_state.radar:
    st.subheader("📋 Carteira sob Vigilância")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v480(t_at)
        if dat:
            p_now = dat['pa']
            lucro = ((p_now / cfg['p_in']) - 1) * 100
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {p_now:,.2f}", f"{lucro:.2f}%")
                if st.button(f"Sair {t_at}", key=f"btn_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. ANÁLISE DETALHADA (Veredito do Mentor image_4b1f9e.jpg)
if st.session_state.consulta_fixa:
    d = analisar_v480(st.session_state.consulta_fixa)
    if d:
        st.divider()
        st.subheader(f"🔍 Análise Profissional: {st.session_state.consulta_fixa}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        
        if d["tem_fund"]:
            upside = ((d['pj']/d['pa'])-1)*100
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}", f"{upside:.1f}% Potencial")
            c3.metric("Dividend Yield", f"{d['div_a']:.2f}%")
            c4.metric("ROE", f"{d['roe']:.1f}%")
            # Veredito do Mentor detalhado
            if d['roe'] > 15:
                st.success(f"✅ **Mentor Sandro:** Esta ação de {d['setor']} é **MUITO BOA**. Entrega lucro real sobre o capital.")
            else:
                st.warning(f"⚠️ **Mentor Sandro:** Atenção. Ativo com margens apertadas. Verifique o setor de {d['setor']}.")
        else:
            c2.metric("Suporte (LTA)", f"R$ {d['sup']:,.2f}")
            c3.metric("Resistência (LTB)", f"R$ {d['res']:,.2f}")
            c4.metric("Div. Mensal Est.", f"{d['div_m']:.3f}%")

        # Histórico e Gráfico (image_4c07e0.png)
        with st.expander("📅 Histórico de Proventos e Gráfico de Tendência", expanded=True):
            if not d["div_hist"].empty:
                st.write("**Dividendos nos últimos 12 meses:**")
                st.table(d["div_hist"].reset_index().rename(columns={'Date':'Data','Dividends':'Valor'}))
            
            fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
            fig.add_trace(go.Scatter(x=d['h'].index, y=d['h']['MA20'], line=dict(color='orange', width=1), name="Média 20d"))
            fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte")
            fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência")
            fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
