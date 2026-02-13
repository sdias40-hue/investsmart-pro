import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Interface Profissional
st.set_page_config(page_title="InvestSmart Pro | Mentor Final", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar Terminal"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE BUSCA OTIMIZADO ---
def buscar_dados_v61(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="60d")
            if not hist.empty:
                return hist, ticker.info, ticker.dividends
        return None, None, None
    except: return None, None, None

# --- 4. RADAR DE SELEÇÃO ---
with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "PETR4", "VALE3"] if aba == "Ações / BDRs" else ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOT-USD"]
    escolha = st.selectbox("Top 5 Recomendadas:", [""] + opcoes)
    ticker_input = st.text_input("Ou digite o Ticker:", "").upper()
    ticker_final = ticker_input if ticker_input else escolha

# --- 5. INTERFACE PRINCIPAL ---
if ticker_final:
    hist, info, divs = buscar_dados_v61(ticker_final)
    
    if hist is not None:
        # Cálculos de Inteligência
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        nome_empresa = info.get('longName', ticker_final)
        setor = info.get('sector', 'Global / Cripto')
        
        st.title(f"🏛️ {nome_empresa}")
        st.caption(f"📍 Setor: {setor} | Ticker: {ticker_final}")

        col1, col2 = st.columns([1, 2.3])
        
        with col1:
            st.subheader("🤖 Mentor IA")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço Atual", f"{simbolo} {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            
            # --- CONVERSOR DE INVESTIMENTO (O que você pediu) ---
            st.write("---")
            st.write("💰 **Simulador de Compra:**")
            valor_invest = st.number_input("Quanto deseja investir (R$)?", min_value=0.0, value=1000.0)
            quantidade = valor_invest / atual
            st.info(f"Com R$ {valor_invest:,.2f}, você compra aproximadamente **{quantidade:.4f}** de {ticker_final}.")

            # PREÇO JUSTO E SAÚDE
            st.divider()
            if "-" not in ticker_final:
                pago_ano = divs.tail(4).sum() if not divs.empty else 0
                preco_justo = (pago_ano / 0.06) if pago_ano > 0 else (info.get('bookValue', 0) * 1.5)
                st.write(f"🎯 **Preço Justo:** {simbolo} {preco_justo:,.2f}")
                st.write(f"📊 **P/L:** {info.get('trailingPE', 'N/A')} | **ROE:** {info.get('returnOnEquity', 0)*100:.1f}%")
            
            # VEREDITO
            if atual > hist['EMA9'].iloc[-1]:
                st.success("✅ GATILHO: Tendência de Alta!")
            else:
                st.error("📉 AGUARDE: Tendência de Baixa.")

        with col2:
            st.subheader("📊 Gráfico Trader Profissional")
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Velas')])
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='Gatilho', line=dict(color='#ffaa00')))
            fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Resistência")
            fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Suporte")
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # 6. CHATBOT MENTOR IA DINÂMICO
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Tire suas dúvidas sobre este ativo:")
        if pergunta:
            # Resposta dinâmica baseada nos dados reais do momento
            msg = f"Analisando '{pergunta}'... O ativo {nome_empresa} está operando em {'alta' if atual > hist.EMA9.iloc[-1] else 'queda'}. "
            msg += f"Graficamente, o suporte importante está em {simbolo} {sup:,.2f}. "
            msg += "Fique atento ao volume de negociação para confirmar o rompimento da resistência."
            st.write(f"**Mentor responde:** {msg}")

    else: st.error(f"Erro ao processar {ticker_final}. Tente novamente.")
else: st.info("👋 Selecione um ativo no Radar Master para começar.")
