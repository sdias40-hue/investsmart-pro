import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="InvestSmart Pro | Terminal Mestre", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login de Segurança
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA OTIMIZADO (Fim do Apagão) ---
def buscar_dados_v60(t):
    try:
        # Tenta rotas para Ações, BDRs e Cripto
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="60d")
            if not hist.empty:
                return hist, ticker.info, ticker.dividends
        return None, None, None
    except: return None, None, None

# --- 4. RADAR DE SELEÇÃO (Top 5 e Digitado) ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    
    # Listas Top 5 (Conforme solicitado)
    opcoes = ["BBAS3", "TAEE11", "VULC3", "PETR4", "VALE3"] if aba == "Ações / BDRs" else ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOT-USD"]
    
    escolha = st.selectbox("Top 5 Recomendadas:", [""] + opcoes)
    ticker_input = st.text_input("Ou digite o Ticker:", "").upper()
    ticker_final = ticker_input if ticker_input else escolha

# --- 5. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestor de Renda")

if ticker_final:
    hist, info, divs = buscar_dados_v60(ticker_final)
    
    if hist is not None:
        # Indicadores Trader
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        ma9 = hist['EMA9'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        
        col1, col2 = st.columns([1, 2.3])
        
        with col1:
            st.subheader("🤖 Veredito do Mentor")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            
            # --- PREÇO JUSTO E SAÚDE FINANCEIRA ---
            st.divider()
            if "-" not in ticker_final:
                pago_ano = divs.tail(4).sum() if not divs.empty else 0
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (info.get('bookValue', 0) * 1.5)
                st.write(f"### 🎯 Preço Justo: {simbolo} {preco_justo:,.2f}")
                
                # Saúde Financeira (P/L e ROE)
                st.write("📊 **Saúde Financeira:**")
                c1, c2 = st.columns(2)
                c1.write(f"**P/L:** {info.get('trailingPE', 'N/A')}")
                c2.write(f"**ROE:** {info.get('returnOnEquity', 0)*100:.1f}%")
            else:
                st.write(f"### 🎯 Suporte do Ciclo: {simbolo} {sup:,.2f}")
                st.info("Ativo Digital: Foco em Acúmulo e Staking.")

            # GATILHO DE COMPRA
            st.divider()
            if atual > ma9:
                st.success("✅ GATILHO ATIVADO: Tendência de Alta!")
                st.write("**Veredito:** 💎 BOA PARA COMPRAR")
            else:
                st.error("📉 AGUARDE: Gráfico em queda.")
                st.write("**Veredito:** ⏳ NÃO COMPENSA AGORA")

        with col2:
            st.subheader("📊 Gráfico Profissional (Candlestick)")
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Velas')])
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='Gatilho', line=dict(color='#ffaa00')))
            # Linhas Trader (Suporte/Resistência)
            fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Resistência")
            fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Suporte")
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # 6. CHATBOT MENTOR IA
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Qual sua dúvida sobre este ativo?")
        if pergunta:
            st.write(f"**Mentor responde:** Sobre '{pergunta}', o ativo está em {'alta' if atual > ma9 else 'queda'}. Com suporte em {simbolo} {sup:,.2f}, mantenha o foco na estratégia de renda.")
    else:
        st.error(f"Erro ao processar {ticker_final}. O servidor da bolsa está instável.")
else:
    st.info("👋 Selecione um ativo nas Top 5 ou digite um Ticker para começar.")
