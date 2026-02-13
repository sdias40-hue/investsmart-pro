import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Terminal de Elite", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. INTELIGÊNCIA DE MERCADO (TOP 5) ---
top_acoes = ["BBAS3.SA", "TAEE11.SA", "VULC3.SA", "PETR4.SA", "JEPP34.SA"]
top_cripto = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD"]
yield_staking = {"SOL-USD": 0.07, "ETH-USD": 0.035, "BNB-USD": 0.025, "ADA-USD": 0.03, "BTC-USD": 0.0}

# --- 4. RADAR DE SELEÇÃO ---
with st.sidebar:
    st.header("🔍 Seleção de Ativos")
    aba = st.radio("Escolha a Categoria:", ["Ações / BDRs", "Criptomoedas"])
    
    if aba == "Ações / BDRs":
        sugestao = st.selectbox("Top 5 Dividendos:", [""] + top_acoes)
    else:
        sugestao = st.selectbox("Top 5 Staking:", [""] + top_cripto)
        
    ticker_input = st.text_input("Ou Digite qualquer Ticker:", "").upper()
    ticker_final = ticker_input if ticker_input else sugestao

# --- 5. MOTOR DE BUSCA ROBUSTO ---
def buscar_dados(t):
    try:
        obj = yf.Ticker(t)
        hist = obj.history(period="60d")
        if hist.empty and ".SA" not in t and "-" not in t:
            obj = yf.Ticker(f"{t}.SA")
            hist = obj.history(period="60d")
        return obj, hist if not hist.empty else None
    except: return None, None

# --- 6. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestor de Oportunidades")

if ticker_final:
    obj, hist = buscar_dados(ticker_final)
    
    if hist is not None:
        # Cálculos de Tendência
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['MA9'].iloc[-1]
        var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        
        col1, col2 = st.columns([1, 1.5], gap="large")
        
        with col1:
            st.subheader("🤖 Analista Sentinela")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            # --- LÓGICA AÇÕES (BAZIN) ---
            if "-" not in ticker_final:
                divs = obj.dividends
                if not divs.empty:
                    pago_ano = divs.tail(4).sum()
                    preco_justo = pago_ano / 0.06
                    st.write(f"### 🎯 Preço Justo: {simbolo} {preco_justo:,.2f}")
                    if atual < preco_justo:
                        st.success("💎 OPORTUNIDADE: Abaixo do preço justo!")
                else: st.info("Buscando histórico de proventos...")

            # --- LÓGICA CRIPTO (STAKING) ---
            else:
                yield_est = yield_staking.get(ticker_final, 0.04) # 4% default
                st.write(f"### ⛏️ Yield de Staking: {yield_est*100:.1f}% a.a.")
                st.info("Preço Justo em cripto é baseado em ciclos de Halving e RSI.")

            # --- TENDÊNCIA GRÁFICA ---
            st.divider()
            if atual > ma9_atual:
                st.success("📈 TENDÊNCIA DE ALTA (Gráfico)")
            else:
                st.error("📉 TENDÊNCIA DE BAIXA (Gráfico)")
                
            if var < -1.5:
                st.warning("🚨 QUEDA DE PREÇO BOA PARA COMPRAR!")

        with col2:
            st.subheader("📊 Gráfico de Tendência (30 dias)")
            chart_data = hist.tail(30).reset_index()
            base = alt.Chart(chart_data).encode(x='Date:T')
            line = base.mark_line(color='#008cff', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
            ma9 = base.mark_line(color='#ffaa00', strokeDash=[5,5]).encode(y='MA9:Q')
            st.altair_chart(line + ma9, use_container_width=True)
            st.caption("🔵 Preço | 🟠 Média Móvel (Tendência)")
            
            if "-" not in ticker_final and not obj.dividends.empty:
                st.write("📋 **Últimos Dividendos:**")
                st.dataframe(obj.dividends.tail(5), use_container_width=True)

    else: st.error("Ativo não encontrado. Tente PETR4 ou SOL-USD.")
else:
    st.info("👋 Selecione um ativo nas listas ao lado ou digite um novo para começar.")

st.caption("InvestSmart Pro v42.0 | Híbrido Ações & Cripto")
