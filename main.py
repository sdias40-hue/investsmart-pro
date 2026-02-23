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
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #d1d5db; }
    .status-box { padding: 20px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ccc; }
    </style>
""", unsafe_allow_html=True)

# 2. Motor de Precisão Sincronizado (Melk3 e Grnd3)
@st.cache_data(ttl=30)
def analisar_v650(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "ETH", "SOL", "XRP"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="1y", interval="1d")
        if h.empty: return None
        
        info = tk.info
        # AJUSTE MELK3: Pegando o Dividend Yield real do ano para bater com simulador
        dy_anual = info.get('dividendYield', 0)
        if dy_anual == 0: # Backup caso o info falhe
            div_hist = tk.actions['Dividends'].last('1y')
            dy_anual = (div_hist.sum() / h['Close'].iloc[-1]) if not div_hist.empty else 0

        # Inteligência Trader (Volatilidade Anualizada)
        vol = h['Close'].pct_change().std() * np.sqrt(252)
        perfil = "🚀 DAY TRADE (Alta Vol)" if vol > 0.40 else "📈 SWING TRADE (Estável)"

        d = {
            "h": h, "ticker": t_up, "pa": h['Close'].iloc[-1], "is_c": is_c,
            "dy": dy_anual, "perfil": perfil, "vol": vol,
            "setor": info.get('sector', 'N/A'),
            "sup": h['Low'].tail(30).min(), "res": h['High'].tail(30).max()
        }
        return d
    except: return None

# --- MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Nexus Command")
    obj_renda = st.number_input("Meta Renda Mensal (R$):", value=1000.0)
    
    with st.form("nexus_form"):
        t_in = st.text_input("Ticker:").upper().strip()
        p_in = st.number_input("Preço de Compra:", min_value=0.0)
        qtd = st.number_input("Quantidade:", min_value=0)
        alvo = st.number_input("Alvo de Venda:", min_value=0.0)
        if st.form_submit_button("🚀 Executar"):
            if t_in:
                st.session_state.radar[t_in] = {"p_in": p_in, "qtd": qtd, "alvo": alvo}
                st.session_state.consulta = t_in; st.rerun()
    
    if st.button("🗑️ Limpar"):
        st.session_state.radar = {}; st.session_state.consulta = None; st.rerun()

# --- PAINEL PRINCIPAL ---
if st.session_state.radar:
    st.subheader("📋 Evolução e Impostos")
    cols = st.columns(3)
    for i, (t_at, cfg) in enumerate(st.session_state.radar.items()):
        dat = analisar_v650(t_at)
        if dat:
            lucro_atual_pct = ((dat['pa'] / cfg['p_in']) - 1) * 100
            # Lucro na Meta e Cálculo de Imposto (15% Swing Trade)
            lucro_bruto = (cfg['alvo'] - cfg['p_in']) * cfg['qtd'] if cfg['alvo'] > cfg['p_in'] else 0
            imposto = lucro_bruto * 0.15 if lucro_bruto > 0 else 0
            
            with cols[i % 3]:
                st.metric(t_at, f"R$ {dat['pa']:,.2f}", f"{lucro_atual_pct:.2f}%")
                if lucro_bruto > 0:
                    st.success(f"Lucro Alvo: R$ {lucro_bruto:,.2f}")
                    st.warning(f"Estimativa IR: R$ {imposto:,.2f}")

if st.session_state.consulta:
    d = analisar_v650(st.session_state.consulta)
    if d:
        st.divider()
        # 1. BLOCO TRADER (Destaque que estava faltando)
        st.subheader(f"⚡ Estratégia Recomendada: {d['perfil']}")
        
        # 2. BLOCO DIVIDENDOS (Cálculo Sincronizado com Simulador)
        # Para R$ 1000 mensal, precisamos de R$ 12.000 anual. 
        # Investimento = 12.000 / Dividend Yield
        if d['dy'] > 0:
            investimento_necessario = (obj_renda * 12) / d['dy']
            q_acoes = investimento_necessario / d['pa']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Capital Necessário", f"R$ {investimento_necessario:,.2f}")
            c2.metric("Quantidade de Ações", f"{int(q_acoes)} un")
            c3.metric("Rendimento Anual (DY)", f"{d['dy']*100:.2f}%")
            st.info(f"💡 Para bater R$ {obj_renda:,.2f}/mês, o capital necessário é R$ {investimento_necessario:,.2f}")

        # 3. GRÁFICO COM LTA/LTB
        fig = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        fig.add_hline(y=d['sup'], line_dash="dash", line_color="green", annotation_text="SUPORTE LTA")
        fig.add_hline(y=d['res'], line_dash="dash", line_color="red", annotation_text="RESISTÊNCIA LTB")
        fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

time.sleep(30)
st.rerun()
