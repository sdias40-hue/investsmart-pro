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

# --- 3. BANCO DE DADOS DE RENDA CRIPTO (STAKING) ---
yield_staking = {
    "SOL-USD": {"yield": 0.07, "freq": "Diário"},
    "ETH-USD": {"yield": 0.035, "freq": "Variável"},
    "BNB-USD": {"yield": 0.026, "freq": "Diário"},
    "ADA-USD": {"yield": 0.03, "freq": "Épocas"}
}

# --- 4. MOTOR DE BUSCA ---
def buscar_dados(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="60d")
            if not hist.empty: return obj, hist, obj.info
        return None, None, None
    except: return None, None, None

# --- 5. RADAR LATERAL ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "JEPP34", "PETR4"] if aba == "Ações / BDRs" else ["SOL-USD", "ETH-USD", "BNB-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_input = st.text_input("Ou digite o Ticker:", "").upper()
    ticker_final = ticker_input if ticker_input else sugestao

# --- 6. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Oportunidades")

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    
    if hist is not None:
        hist['MA9'] = hist['Close'].rolling(window=9).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['MA9'].iloc[-1]
        var = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        
        col1, col2 = st.columns([1, 1.4], gap="large")
        
        with col1:
            st.subheader("🤖 Mentor InvestSmart")
            simbolo = "US$" if "USD" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{var:.2f}%")
            
            st.divider()
            st.write("### 📜 Conselho do Mentor")
            
            # LÓGICA DE GATILHO PARA QUEM NÃO ENTENDE DE GRÁFICO
            if atual > ma9_atual:
                st.success("✅ GATILHO ATIVADO: O gráfico reagiu! O preço cruzou a média para cima. Momento favorável.")
            else:
                st.error("⚠️ AGUARDE: O gráfico ainda não reagiu. O preço está abaixo da média de segurança.")

            # EXIBIÇÃO DE RENDA (AÇÕES OU CRIPTO)
            if "-" not in ticker_final:
                divs = obj.dividends
                if not divs.empty:
                    pago_ano = divs.tail(4).sum()
                    st.write(f"**Renda (Dividendos):** {simbolo} {pago_ano:,.2f} no último ano.")
                    st.write(f"**Preço Justo:** {simbolo} {pago_ano/0.06:,.2f}")
            else:
                # Informações de Staking para Cripto
                dados_s = yield_staking.get(ticker_final, {"yield": 0.04, "freq": "Diário"})
                st.write(f"### ⛏️ Renda (Staking)")
                st.write(f"**Retorno Anual:** {dados_s['yield']*100:.1f}% a.a.")
                st.write(f"**Pagamento:** {dados_s['freq']}")
                st.info("Criptomoedas geram novas moedas como recompensa (Staking), similar a dividendos.")

        with col2:
            st.subheader("📊 Gráfico de Tendência")
            chart_data = hist.tail(30).reset_index()
            base = alt.Chart(chart_data).encode(x='Date:T')
            line = base.mark_line(color='#008cff', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
            ma9_line = base.mark_line(color='#ffaa00', strokeDash=[5,5]).encode(y='MA9:Q')
            st.altair_chart(line + ma9_line, use_container_width=True)
            st.caption("🔵 Preço | 🟠 Média de Segurança (Gatilho)")

    # --- ESPAÇO PARA O FUTURO CHATBOT ---
    st.divider()
    st.subheader("💬 Mentor IA Chat (Em breve)")
    st.text_input("Faça uma pergunta para a IA sobre este ativo:", disabled=True, placeholder="Em breve você poderá tirar dúvidas aqui...")

else:
    st.info("👋 Selecione um ativo ao lado para iniciar a análise.")
