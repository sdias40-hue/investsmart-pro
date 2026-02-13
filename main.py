import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Setup
st.set_page_config(page_title="InvestSmart Pro | Preço Justo", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA COM INTELIGÊNCIA ---
def buscar_dados(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="200d") # 200 dias para Preço Justo Cripto
            if not hist.empty: return obj, hist, obj.info
        return None, None, None
    except: return None, None, None

# --- 4. RADAR ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "MXRF11", "JEPP34"] if aba == "Ações / BDRs" else ["BTC-USD", "SOL-USD", "ETH-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_input = st.text_input("Digite o Ticker:", "").upper()
    ticker_final = ticker_input if ticker_input else sugestao

# --- 5. INTERFACE ---
if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    
    if hist is not None:
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        hist['MA200'] = hist['Close'].rolling(window=200).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['MA9'].iloc[-1]
        
        col1, col2 = st.columns([1, 1.4])
        
        with col1:
            st.subheader("🤖 Veredito do Preço Justo")
            simbolo = "US$" if "USD" in ticker_final else "R$"
            st.metric(f"Preço Atual", f"{simbolo} {atual:,.2f}")
            
            # --- CÁLCULO UNIVERSAL DE PREÇO JUSTO ---
            st.divider()
            
            if "-" not in ticker_final: # AÇÕES E BDRS
                divs = obj.dividends
                pago_ano = divs.tail(4).sum() if not divs.empty else 0
                vpa = info.get('bookValue', 0)
                
                # Prioridade 1: Bazin (Dividendos) | Prioridade 2: Graham (Patrimônio)
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (vpa * 1.5 if vpa > 0 else atual * 0.9)
                
                st.write(f"### 🎯 Preço Justo Estimado: {simbolo} {preco_justo:,.2f}")
                if atual < preco_justo:
                    st.success("✅ OPORTUNIDADE: Abaixo do valor justo!")
                else:
                    st.warning("❌ ALERTA: Acima do valor justo.")
            
            else: # CRIPTOMOEDAS
                ma200 = hist['MA200'].iloc[-1]
                # Preço Justo Cripto: Geralmente próximo à média de 200 dias no ciclo
                preco_justo_cripto = ma200 * 1.2 
                st.write(f"### 🎯 Preço Justo (Ciclo): US$ {preco_justo_cripto:,.2f}")
                if atual < preco_justo_cripto:
                    st.success("✅ ZONA DE ACÚMULO: Preço atrativo para Staking.")
                else:
                    st.error("⚠️ ZONA DE RISCO: Ativo esticado graficamente.")

            # --- GATILHO DE COMPRA ---
            if atual > ma9_atual:
                st.info("📈 GATILHO: Gráfico em alta. Confirmado!")
            else:
                st.error("📉 AGUARDE: Tendência de queda no curto prazo.")

        with col2:
            st.subheader("📊 Gráfico Analítico")
            chart_data = hist.tail(50).reset_index()
            base = alt.Chart(chart_data).encode(x='Date:T')
            line = base.mark_line(color='#008cff', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
            ma9_line = base.mark_line(color='#ffaa00', strokeDash=[5,5]).encode(y='MA9:Q')
            st.altair_chart(line + ma9_line, use_container_width=True)
            st.caption("🔵 Preço | 🟠 Média de Gatilho")
    else:
        st.error("Ativo não encontrado. Tente PETR4 ou BTC-USD.")
else:
    st.info("👋 Radar aguardando. Selecione um ativo para ver o Preço Justo.")
