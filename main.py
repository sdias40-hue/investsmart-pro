import streamlit as st
import yfinance as yf
import pandas as pd

# Tenta carregar o gráfico profissional, senão usa o padrão
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# 1. Estilo Profissional
st.set_page_config(page_title="InvestSmart Pro | Gestor de Renda", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Acesso ao Terminal:", type="password")
    if st.button("Abrir"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA ROBUSTO ---
def buscar_dados(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            obj = yf.Ticker(s)
            hist = obj.history(period="60d")
            if not hist.empty: return obj, hist, obj.info
        return None, None, None
    except: return None, None, None

# --- 4. RADAR DE SELEÇÃO ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "MXRF11", "JEPP34"] if aba == "Ações / BDRs" else ["SOL-USD", "ETH-USD", "BTC-USD"]
    sugestao = st.selectbox("Favoritos:", [""] + opcoes)
    ticker_final = st.text_input("Ou digite o Ticker:", "").upper() or sugestao

# --- 5. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Analista de Renda")

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    if hist is not None:
        # Cálculos de Inteligência
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        ma9_atual = hist['EMA9'].iloc[-1]
        volatilidade = hist['Close'].pct_change().std() * 100
        var_dia = ((atual / hist['Close'].iloc[-2]) - 1) * 100
        
        col1, col2 = st.columns([1, 1.4])
        
        with col1:
            st.subheader("🤖 Mentor InvestSmart")
            setor = info.get('sector', 'Global / Cripto')
            st.caption(f"📍 Setor: {setor}")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{var_dia:.2f}%")
            
            st.divider()
            
            # --- A: ANÁLISE DE PERFIL ---
            if volatilidade > 2.2:
                st.error("⚠️ PERFIL: INVESTIDOR AGRESSIVO (Alta Volatilidade)")
            else:
                st.success("🛡️ PERFIL: INVESTIDOR CONSERVADOR (Estável)")

            # --- B: ANÁLISE DE RESULTADOS (QUALIDADE) ---
            margem = info.get('profitMargins', 0)
            if margem > 0.10:
                st.info("💎 RESULTADOS: Empresa lucrativa e eficiente.")
            elif "-" in ticker_final:
                st.info("🌐 CRIPTO: Ativo de alta demanda tecnológica.")
            else:
                st.warning("🧐 ATENÇÃO: Margens baixas. Analise o endividamento.")

            # --- C: CONSELHO & GATILHO ---
            st.divider()
            st.write("### 📜 Veredito Final")
            
            pago_ano = obj.dividends.tail(4).sum() if not obj.dividends.empty else 0
            preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (info.get('bookValue', 0) * 1.5)
            
            if atual < preco_justo and atual > ma9_atual:
                st.success("✅ COMPENSA: Ativo barato e com gráfico reagindo!")
            elif atual < preco_justo:
                st.warning("⏳ PREÇO BOM, MAS AGUARDE: Gráfico ainda em queda.")
            else:
                st.error("❌ NÃO COMPENSA: Preço acima do valor justo.")
            
            if pago_ano > 0: st.write(f"**Preço Justo (Bazin):** {simbolo} {preco_justo:,.2f}")

        with col2:
            st.subheader("📊 Gráfico Profissional")
            if PLOTLY_AVAILABLE:
                fig = go.Figure(data=[go.Candlestick(
                    x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'], name='Velas'
                )])
                fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], mode='lines', name='Média Gatilho', line=dict(color='#ffaa00')))
                fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Instale 'plotly' para ver as Velas (Candles).")
                st.line_chart(hist['Close'])

    # --- RESERVA CHATBOT ---
    st.divider()
    st.subheader("💬 Chatbot Mentor (Mentoria Staking)")
    st.info("Espaço reservado para dúvidas sobre renda passiva digital.")

else:
    st.info("👋 Selecione um ativo para ver a análise massiva.")
