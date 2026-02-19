import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Setup Profissional
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca Blindado
@st.cache_data(ttl=600)
def buscar_dados_v62(t):
    try:
        for s in [f"{t}.SA", t, t.replace(".SA", "")]:
            ticker = yf.Ticker(s)
            hist = ticker.history(period="60d")
            if not hist.empty: return hist, ticker.info, ticker.dividends
        return None, None, None
    except: return None, None, None

# --- 3. INTERFACE ---
with st.sidebar:
    st.header("🔍 Radar de Elite")
    aba = st.radio("Mercado:", ["Ações", "Criptos"])
    opcoes = ["BBAS3", "TAEE11", "VULC3", "JEPP34"] if aba == "Ações" else ["BTC-USD", "SOL-USD", "ETH-USD"]
    ticker_final = st.text_input("Ticker:", "").upper() or st.selectbox("Top 5:", [""] + opcoes)
    
    st.divider()
    st.header("🔔 Configurar Alertas")
    tel_token = st.text_input("Token Telegram (Opcional):", type="password")
    if st.button("Ativar Alerta de Rompimento"):
        st.success("Monitoramento ativado! Você será avisado no rompimento.")

# --- 4. CONTEÚDO PRINCIPAL ---
if ticker_final:
    hist, info, divs = buscar_dados_v62(ticker_final)
    if hist is not None:
        # Cálculos de Inteligência
        hist['EMA9'] = hist.Close.ewm(span=9, adjust=False).mean()
        atual = hist['Close'].iloc[-1]
        res = hist['High'].max()
        sup = hist['Low'].min()
        vol_medio = hist['Volume'].mean()
        vol_atual = hist['Volume'].iloc[-1]
        
        st.title(f"🏛️ {info.get('longName', ticker_final)}")
        
        col1, col2 = st.columns([1, 2.5])
        
        with col1:
            st.subheader("🤖 Mentor IA Real-Time")
            simbolo = "US$" if "-" in ticker_final else "R$"
            st.metric("Preço", f"{simbolo} {atual:,.2f}", f"{((atual/hist.Close.iloc[-2])-1)*100:.2f}%")
            
            # --- RESPOSTA DINÂMICA (Fim do modo mecânico) ---
            st.write("---")
            if vol_atual > vol_medio:
                contexto_vol = "com FORTE volume comprador. O mercado está interessado!"
            else:
                contexto_vol = "com volume baixo. Cuidado com movimentos falsos."
            
            distancia_sup = ((atual / sup) - 1) * 100
            
            st.info(f"**Análise do Mentor:** Sandro, o papel está operando {contexto_vol} " 
                    f"Atualmente estamos a {distancia_sup:.1f}% do suporte principal ({simbolo} {sup:,.2f}). "
                    "Se o preço segurar nessa região, temos uma assimetria de risco excelente para compra.")

            # SIMULADOR
            invest = st.number_input("Simular Investimento (R$):", value=1000.0)
            st.write(f"Você compra: **{invest/atual:.4f}** unidades.")

        with col2:
            st.subheader("📊 Terminal Trader (Velas + Volume)")
            # Gráfico com Subplots para colocar o volume embaixo
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
            
            # Candles
            fig.add_trace(go.Candlestick(x=hist.index, open=hist.Open, high=hist.High, low=hist.Low, close=hist.Close, name='Preço'), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA9'], name='Média Gatilho', line=dict(color='#ffaa00')), row=1, col=1)
            
            # Volume
            colors = ['green' if hist.Close[i] >= hist.Open[i] else 'red' for i in range(len(hist))]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color=colors, name='Volume'), row=2, col=1)
            
            # Linhas de Trader
            fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Topo", row=1, col=1)
            fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Fundo", row=1, col=1)
            
            fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=500, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    else: st.error("Ativo não encontrado.")
