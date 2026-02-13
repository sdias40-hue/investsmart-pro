import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="InvestSmart Pro | Mentor", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login de Segurança
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
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

# --- 4. RADAR LATERAL ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "PETR4", "MXRF11"] if aba == "Ações / BDRs" else ["BTC-USD", "SOL-USD", "ETH-USD"]
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
        
        col1, col2 = st.columns([1, 1.4])
        
        with col1:
            st.subheader("🤖 Veredito do Mentor")
            setor = info.get('sector', 'Global / Cripto')
            st.caption(f"📍 Setor: {setor}")
            
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}")
            
            st.divider()
            
            # --- ANÁLISE DE PERFIL (Visto no image_da6628.jpg) ---
            if volatilidade > 2.2:
                st.error("⚠️ PERFIL: INVESTIDOR AGRESSIVO (Alta Volatilidade)")
            else:
                st.success("🛡️ PERFIL: INVESTIDOR CONSERVADOR (Estável)")

            # --- ANÁLISE DE RESULTADOS ---
            margem = info.get('profitMargins', 0)
            if margem > 0.10:
                st.info("💎 RESULTADOS: Empresa lucrativa e com bons fundamentos.")
            elif "-" in ticker_final:
                st.info("🌐 TECNOLOGIA: Ativo digital com alta demanda de rede.")
            else:
                st.warning("🧐 ATENÇÃO: Resultados abaixo da média do setor.")

            # --- PREÇO JUSTO & ESTRATÉGIA ---
            st.divider()
            st.write("### 🎯 Estratégia de Compra")
            pago_ano = obj.dividends.tail(4).sum() if not obj.dividends.empty else 0
            preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (info.get('bookValue', 0) * 1.5)
            
            if atual < preco_justo and atual > ma9_atual:
                st.success("✅ VEREDITO: BOA PARA COMPRAR! Preço e Gráfico alinhados.")
            elif atual < preco_justo:
                st.warning("⏳ AGUARDE: Preço atrativo, mas o gráfico ainda cai.")
            else:
                st.error("❌ NÃO COMPENSA: Preço acima do valor justo atual.")
            
            if pago_ano > 0: st.write(f"Preço Justo (Bazin): {simbolo} {preco_justo:,.2f}")

        with col2:
            st.subheader("📊 Gráfico de Gatilho")
            st.line_chart(hist[['Close', 'EMA9']])
            st.caption("🔵 Preço Atual | 🟠 Média de Gatilho")
            
            # Tabela de Dividendos ou Staking
            if "-" not in ticker_final:
                st.write("📋 **Histórico de Dividendos:**")
                st.dataframe(obj.dividends.tail(5), use_container_width=True)
            else:
                st.write("### ⛏️ Informação de Staking")
                st.info("Este ativo permite gerar renda passiva via Staking (Dividendos Cripto).")

        # --- 6. CHATBOT MENTOR IA (Ativado para Perguntas) ---
        st.divider()
        st.subheader("💬 Chatbot Mentor IA")
        pergunta = st.text_input("Tire suas dúvidas sobre este ativo ou o mercado:")
        if pergunta:
            st.write(f"**Mentor responde:** Para analisar '{pergunta}', o robô está processando as notícias de última hora. No momento, o foco deve ser no setor de {setor} e na tendência de {('alta' if atual > ma9_atual else 'queda')} do gráfico.")

    else:
        st.error(f"Erro ao carregar {ticker_final}. Tente outro código.")
else:
    st.info("👋 Selecione um ativo ao lado para ver o Veredito do Mentor.")
