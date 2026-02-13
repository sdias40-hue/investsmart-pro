import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Trader Edition", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Login
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    senha = st.text_input("Chave Mestra:", type="password")
    if st.button("Acessar"):
        if senha == "sandro2026": st.session_state['auth'] = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE ANÁLISE TRADER ---
def buscar_dados(t):
    for s in [f"{t}.SA", t, t.replace(".SA", "")]:
        obj = yf.Ticker(s); h = obj.history(period="60d")
        if not h.empty: return obj, h, obj.info
    return None, None, None

# --- 4. INTERFACE PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Trader")

with st.sidebar:
    st.header("🔍 Radar Master")
    aba = st.radio("Categoria:", ["Ações / BDRs", "Criptomoedas"])
    opcoes = ["VULC3", "BBAS3", "TAEE11", "SOL-USD"]
    ticker_final = st.text_input("Digite o Ticker:", "").upper() or st.selectbox("Favoritos:", [""] + opcoes)

if ticker_final:
    obj, hist, info = buscar_dados(ticker_final)
    if hist is not None:
        # Cálculos Técnicos
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        ma9 = hist['EMA9'].iloc[-1]
        
        # Identificando Suporte e Resistência (Mínimas e Máximas do período)
        resistencia = hist['High'].max()
        suporte = hist['Low'].min()
        
        col1, col2 = st.columns([1, 2.3])
        with col1:
            st.subheader("🤖 Mentor IA Trader")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric(f"Preço {ticker_final}", f"{simbolo} {atual:,.2f}")
            
            # RESPOSTA DINÂMICA DA IA
            st.divider()
            if atual > ma9:
                status_grafico = "em clara tendência de ALTA"
                conselho = "O momentum é comprador. Atenção à resistência."
            else:
                status_grafico = "em fase de CORREÇÃO"
                conselho = "Aguarde o preço superar a média amarela para confirmar entrada."

            st.write(f"### 🎯 Veredito")
            if atual > ma9 and atual < resistencia * 0.95:
                st.success(f"O ativo está {status_grafico}. {conselho}")
            else:
                st.warning(f"Cuidado: Ativo {status_grafico}. Suporte em {simbolo} {suporte:,.2f}")

        with col2:
            st.subheader("📊 Gráfico com Linhas de Análise")
            fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Candles')])
            
            # Linha de Média Móvel (Gatilho)
            fig.add_trace(go.Scatter(x=hist.index, y=hist.EMA9, name='Gatilho', line=dict(color='#ffaa00', width=2)))
            
            # Linhas de Trader (Suporte e Resistência)
            fig.add_hline(y=resistencia, line_dash="dot", line_color="red", annotation_text="Resistência (Topo)")
            fig.add_hline(y=suporte, line_dash="dot", line_color="green", annotation_text="Suporte (Fundo)")
            
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=450)
            st.plotly_chart(fig, use_container_width=True)

        # 5. CHATBOT COM RESPOSTAS VARIADAS (Baseado em Lógica)
        st.divider()
        st.subheader("💬 Mentor IA Chat")
        pergunta = st.text_input("Pergunte algo sobre este ativo:")
        if pergunta:
            # Aqui simulamos uma resposta variada baseada nos dados reais
            distancia_topo = ((resistencia / atual) - 1) * 100
            st.write(f"**Mentor responde:** Sobre '{pergunta}', observe que o ativo está a {distancia_topo:.1f}% da sua resistência principal. O setor de {info.get('sector', 'Global')} está volátil, então foque no suporte de {simbolo} {suporte:,.2f} para proteção.")

else: st.info("👋 Selecione um ativo para iniciar a análise trader.")
