import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt

# 1. Configuração e Estilo
st.set_page_config(page_title="InvestSmart Pro | Gestor de Risco", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA (Blindado para JEPP34 e outros) ---
def buscar_dados(t):
    try:
        # Tenta rotas alternativas para capturar ativos difíceis
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="60d")
            if not hist.empty: return obj, hist
        return None, None
    except: return None, None

# --- 4. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestor de Risco e Renda")

with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "JEPP34", "PETR4"] if aba == "Ações / BDRs" else ["SOL-USD", "BTC-USD", "ETH-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_input = st.text_input("Ou digite o Ticker:", "").upper()
    ticker_final = ticker_input if ticker_input else sugestao

if ticker_final:
    obj, hist = buscar_dados(ticker_final)
    
    if hist is not None:
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['MA9'].iloc[-1]
        var_diaria = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        # Cálculo de volatilidade (desvio padrão dos últimos 20 dias)
        volatilidade = hist['Close'].pct_change().std() * 100
        
        col1, col2 = st.columns([1, 1.4], gap="large")
        
        with col1:
            st.subheader("🤖 Veredito do Mentor")
            simbolo = "US$" if "USD" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{var_diaria:.2f}%")
            
            st.divider()
            
            # --- ANÁLISE DE PERFIL DE RISCO ---
            if volatilidade > 2.5:
                st.error("⚠️ PERFIL: INVESTIDOR AGRESSIVO (Alta Volatilidade)")
            else:
                st.success("🛡️ PERFIL: INVESTIDOR CONSERVADOR (Estável)")

            # --- VEREDITO DE COMPRA ---
            st.write("### 📜 Estratégia de Compra")
            
            if "-" not in ticker_final: # Lógica para Ações/BDRs
                divs = obj.dividends
                pago_ano = divs.tail(4).sum() if not divs.empty else 0
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else 0
                
                if pago_ano > 0:
                    if atual < preco_justo and atual > ma9_atual:
                        st.success("✅ VEREDITO: BOA PARA COMPRAR! Fundamentos e gráfico alinhados.")
                    elif atual < preco_justo:
                        st.info("⏳ VEREDITO: AGUARDE REAÇÃO. Preço está bom, mas gráfico ainda cai.")
                    else:
                        st.warning("❌ VEREDITO: NÃO COMPENSA AGORA. Preço acima do valor justo.")
                else:
                    st.warning("🔍 ATENÇÃO: Ativo focado em crescimento, não em dividendos.")
            else: # Lógica para Criptos
                if atual > ma9_atual:
                    st.success("✅ VEREDITO: MOMENTO DE ENTRADA. Tendência de alta confirmada.")
                else:
                    st.error("❌ VEREDITO: NÃO COMPENSA. Aguarde o fim da queda.")

        with col2:
            st.subheader("📊 Gráfico Analítico")
            chart_data = hist.tail(30).reset_index()
            base = alt.Chart(chart_data).encode(x='Date:T')
            line = base.mark_line(color='#008cff', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
            ma9_line = base.mark_line(color='#ffaa00', strokeDash=[5,5]).encode(y='MA9:Q')
            st.altair_chart(line + ma9_line, use_container_width=True)
            st.caption("🔵 Preço Atual | 🟠 Média de Segurança (Gatilho)")

    st.divider()
    st.caption("InvestSmart Pro v45.0 | Analista de Risco e Oportunidade")

else:
    st.info("👋 Selecione um ativo ao lado para ver o Veredito do Mentor.")
