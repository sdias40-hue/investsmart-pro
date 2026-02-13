import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Gestor Master", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA COM INTELIGÊNCIA DE SETOR ---
def buscar_dados_completos(t):
    try:
        # Tripla tentativa de ticker para evitar erro 404 em BDRs
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="60d")
            if not hist.empty:
                # Captura o setor e info da empresa
                info = obj.info
                return obj, hist, info
        return None, None, None
    except: return None, None, None

# --- 4. RADAR DE SELEÇÃO ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    
    opcoes = ["BBAS3", "TAEE11", "VULC3", "JEPP34", "PETR4"] if aba == "Ações / BDRs" else ["BTC-USD", "ETH-USD", "SOL-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_input = st.text_input("Ou digite o Ticker:", "").upper()
    ticker_final = ticker_input if ticker_input else sugestao

# --- 5. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Analista Híbrido")

if ticker_final:
    obj, hist, info = buscar_dados_completos(ticker_final)
    
    if hist is not None:
        # Cálculos de Tendência Gráfica
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['MA9'].iloc[-1]
        var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        
        col1, col2 = st.columns([1, 1.4], gap="large")
        
        with col1:
            st.subheader("🤖 Mentor InvestSmart")
            # Identificação de Setor
            setor = info.get('sector', 'Setor Global / Cripto')
            st.caption(f"📍 Setor: {setor}")
            
            simbolo = "US$" if "USD" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            # --- CONSELHO FUNDAMENTALISTA ---
            st.divider()
            st.write("### 📜 Conselho do Mentor")
            
            # Lógica para Ações/BDRs
            if "-" not in ticker_final:
                divs = obj.dividends
                if not divs.empty:
                    pago_ano = divs.tail(4).sum()
                    preco_justo = pago_ano / 0.06
                    
                    # Confluência de Sinais
                    if atual < preco_justo and atual > ma9_atual:
                        st.success("💎 OPORTUNIDADE DE OURO: Ativo barato e em tendência de alta!")
                    elif atual < preco_justo:
                        st.info("🐢 FUNDAMENTALISTA: Barato, mas aguarde o gráfico reagir.")
                    elif atual > ma9_atual:
                        st.warning("🚀 MOMENTUM: Gráfico subindo, mas preço acima do justo.")
                    else:
                        st.error("❌ ALERTA: Caro e em queda. Fique de fora.")
                    
                    st.write(f"**Preço Justo (Bazin):** {simbolo} {preco_justo:,.2f}")
                else:
                    st.write("Ativo em fase de crescimento. Foco em ganho de capital.")
            
            # Lógica para Criptos
            else:
                if atual > ma9_atual:
                    st.success("🔥 CRIPTO ALERTA: Tendência de alta confirmada no curto prazo.")
                else:
                    st.error("❄️ CRIPTO ALERTA: Tendência de queda. Risco de Staking.")

        with col2:
            st.subheader("📊 Gráfico de Tendência (Analista)")
            chart_data = hist.tail(30).reset_index()
            base = alt.Chart(chart_data).encode(x='Date:T')
            line = base.mark_line(color='#008cff', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
            ma9_line = base.mark_line(color='#ffaa00', strokeDash=[5,5]).encode(y='MA9:Q')
            st.altair_chart(line + ma9_line, use_container_width=True)
            
            if "-" not in ticker_final and not obj.dividends.empty:
                st.write("📋 **Histórico de Dividendos Recentes:**")
                st.dataframe(obj.dividends.tail(5).to_frame().sort_index(ascending=False), use_container_width=True)
    else:
        st.error(f"Erro na comunicação com {ticker_final}. Tente CMIG4 ou SOL-USD.")
else:
    st.info("👋 Radar Master aguardando. Selecione um ativo para ver o Conselho do Mentor.")
