import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (image_d4d43a.png)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Precisão Trader e Dividendos (Sincronizado image_e4c01e.png)
@st.cache_data(ttl=60)
def analisar_v640(t):
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
        
        # Sincronização MELK3: Média Mensal Real (image_e4c01e.png)
        renda_mensal_por_acao = total_pago_12m / 12 if total_pago_12m > 0 else 0

        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_12m": total_pago_12m, "div_mensal": renda_mensal_por_acao,
            "setor": info.get('sector', 'N/A'), "roe": (info.get('returnOnEquity', 0) or 0) * 100
        }

        # Especialidade Trader: Volatilidade (image_d69d3b.jpg)
        h['Vol'] = h['Close'].pct_change().std() * np.sqrt(252)
        d["perfil_trader"] = "Day Trader" if h['Vol'].iloc[-1] > 0.45 else "Swing Trader"
        
        # Graham (image_e20607.png)
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Canais LTA/LTB (image_4c07e0.png)
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_fixa' not in st.session_state: st.session_state.consulta_fixa = None

# --- SIDEBAR: NEXUS COMMAND (image_4c1edf.png) ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    meta_renda = st.number_input("Objetivo Renda Mensal (R$):", min_value=0.0, value=1000.0)
    
    with st.form("form_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, MELK3, BTC):").upper().strip()
        is_cripto = t_in in ["BTC", "ETH", "SOL", "XRP"]
        
        if is_cripto:
            p_compra = st.number_input("Preço Entrada (US$):", min_value=0.0, format="%.4f")
            val_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            qtd = 0
        else:
            p_compra = st.number_input("Preço Compra (R$):", min_value=0.0)
            qtd = st.number_input("Quantidade Atual:", min_value=0, step=1)
            
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        if st.form_submit_button("🚀 Monitorar e Consultar"):
            if t_in:
                st.session_state.radar[t_in] = {"p_in": p_compra, "qtd": qtd, "alvo": alvo, "is_c": is_cripto}
                st.session_state.consulta_fixa = t_in; st.rerun()

    if st.button("🗑️ Limpar Registro"):
        st.session_state.radar, st.session_state.consulta_fixa = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. MONITORAMENTO (Evolução e Lucro na Meta image_e4c47d.png)
if st.session_state.radar:
    st.subheader("📋 Evolução do Patrimônio")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v640(t_at)
        if dat:
            p_now = dat['pa']
            evolucao = ((p_now / cfg['p_in']) - 1) * 100
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {p_now:,.2f}", f"{evolucao:.2f}% (Evolução)")
                if not cfg.get('is_c', False):
                    lucro_meta = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > 0 else 0
                    st.caption(f"💰 Lucro na Meta: R$ {lucro_meta:,.2f} | 🎯 Alvo: R$ {cfg['alvo']:.2f}")
                if st.button(f"Sair {t_at}", key=f"del_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. INTELIGÊNCIA DE MERCADO (Sincronizado image_e4c01e.png)
if st.session_state.consulta_fixa:
    d = analisar_v640(st.session_state.consulta_fixa)
    if d:
        st.divider()
        st.subheader(f"🔍 Nexus Intelligence: {d['ticker']}")
        
        # Simulador de Renda (Correção MELK3 bater com simuladores externos)
        if not d['is_c'] and d['div_mensal'] > 0:
            acoes_meta = int(meta_renda / d['div_mensal'])
            capital_total = acoes_meta * d['pa']
            s1, s2, s3 = st.columns(3)
            s1.metric("Ações p/ Meta", f"{acoes_meta} un")
            s2.metric("Capital Necessário", f"R$ {capital_total:,.2f}")
            s3.metric("Renda Mensal Alvo", f"R$ {meta_renda:,.2f}")
            st.info(f"💡 Para renda de R$ {meta_renda:,.2f}, invista aproximadamente R$ {capital_total:,.2f} em {d['ticker']}.")

        # Perfil Trader e Métricas (image_d69d3b.jpg)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Perfil Sugerido", d["perfil_trader"])
        c3.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
        c4.metric("ROE", f"{d['roe']:.1f}%")
        
        # Gráfico com Canais LTA/LTB (image_4c07e0.png)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte LTA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência LTB")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()mport streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# 1. Configuração de Interface Premium (image_d4d43a.png)
st.set_page_config(page_title="Nexus Invest Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Precisão Trader e Dividendos (Sincronizado image_e4c01e.png)
@st.cache_data(ttl=60)
def analisar_v640(t):
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
        
        # Sincronização MELK3: Média Mensal Real (image_e4c01e.png)
        renda_mensal_por_acao = total_pago_12m / 12 if total_pago_12m > 0 else 0

        d = {
            "h": h, "info": info, "is_c": is_c, "ticker": t_up, "pa": h['Close'].iloc[-1],
            "div_12m": total_pago_12m, "div_mensal": renda_mensal_por_acao,
            "setor": info.get('sector', 'N/A'), "roe": (info.get('returnOnEquity', 0) or 0) * 100
        }

        # Especialidade Trader: Volatilidade (image_d69d3b.jpg)
        h['Vol'] = h['Close'].pct_change().std() * np.sqrt(252)
        d["perfil_trader"] = "Day Trader" if h['Vol'].iloc[-1] > 0.45 else "Swing Trader"
        
        # Graham (image_e20607.png)
        lpa, vpa = info.get('forwardEps'), info.get('bookValue')
        d["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa and vpa and not is_c else 0
        
        # Canais LTA/LTB (image_4c07e0.png)
        d["sup"] = h['Low'].tail(30).min()
        d["res"] = h['High'].tail(30).max()
        return d
    except: return None

# --- ESTADOS DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta_fixa' not in st.session_state: st.session_state.consulta_fixa = None

# --- SIDEBAR: NEXUS COMMAND (image_4c1edf.png) ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    meta_renda = st.number_input("Objetivo Renda Mensal (R$):", min_value=0.0, value=1000.0)
    
    with st.form("form_nexus", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, MELK3, BTC):").upper().strip()
        is_cripto = t_in in ["BTC", "ETH", "SOL", "XRP"]
        
        if is_cripto:
            p_compra = st.number_input("Preço Entrada (US$):", min_value=0.0, format="%.4f")
            val_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            qtd = 0
        else:
            p_compra = st.number_input("Preço Compra (R$):", min_value=0.0)
            qtd = st.number_input("Quantidade Atual:", min_value=0, step=1)
            
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        
        if st.form_submit_button("🚀 Monitorar e Consultar"):
            if t_in:
                st.session_state.radar[t_in] = {"p_in": p_compra, "qtd": qtd, "alvo": alvo, "is_c": is_cripto}
                st.session_state.consulta_fixa = t_in; st.rerun()

    if st.button("🗑️ Limpar Registro"):
        st.session_state.radar, st.session_state.consulta_fixa = {}, None; st.rerun()

# --- PAINEL PRINCIPAL ---
# 1. MONITORAMENTO (Evolução e Lucro na Meta image_e4c47d.png)
if st.session_state.radar:
    st.subheader("📋 Evolução do Patrimônio")
    m_cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v640(t_at)
        if dat:
            p_now = dat['pa']
            evolucao = ((p_now / cfg['p_in']) - 1) * 100
            with m_cols[i % 3]:
                st.metric(t_at, f"R$ {p_now:,.2f}", f"{evolucao:.2f}% (Evolução)")
                if not cfg.get('is_c', False):
                    lucro_meta = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > 0 else 0
                    st.caption(f"💰 Lucro na Meta: R$ {lucro_meta:,.2f} | 🎯 Alvo: R$ {cfg['alvo']:.2f}")
                if st.button(f"Sair {t_at}", key=f"del_{t_at}"):
                    del st.session_state.radar[t_at]; st.rerun()

# 2. INTELIGÊNCIA DE MERCADO (Sincronizado image_e4c01e.png)
if st.session_state.consulta_fixa:
    d = analisar_v640(st.session_state.consulta_fixa)
    if d:
        st.divider()
        st.subheader(f"🔍 Nexus Intelligence: {d['ticker']}")
        
        # Simulador de Renda (Correção MELK3 bater com simuladores externos)
        if not d['is_c'] and d['div_mensal'] > 0:
            acoes_meta = int(meta_renda / d['div_mensal'])
            capital_total = acoes_meta * d['pa']
            s1, s2, s3 = st.columns(3)
            s1.metric("Ações p/ Meta", f"{acoes_meta} un")
            s2.metric("Capital Necessário", f"R$ {capital_total:,.2f}")
            s3.metric("Renda Mensal Alvo", f"R$ {meta_renda:,.2f}")
            st.info(f"💡 Para renda de R$ {meta_renda:,.2f}, invista aproximadamente R$ {capital_total:,.2f} em {d['ticker']}.")

        # Perfil Trader e Métricas (image_d69d3b.jpg)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço Atual", f"R$ {d['pa']:,.2f}")
        c2.metric("Perfil Sugerido", d["perfil_trader"])
        c3.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
        c4.metric("ROE", f"{d['roe']:.1f}%")
        
        # Gráfico com Canais LTA/LTB (image_4c07e0.png)
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="Suporte LTA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="Resistência LTB")
        fig.update_layout(height=450, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
