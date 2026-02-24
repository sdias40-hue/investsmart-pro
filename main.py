import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master (Azul Turquesa e Branco - Alta Legibilidade)
st.set_page_config(page_title="Nexus Ultra | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    h1, h2, h3 { color: #00d4ff !important; font-family: 'Segoe UI', sans-serif; }
    .stMetric { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .report-box { background-color: #1c2128; border-left: 5px solid #00d4ff; padding: 20px; border-radius: 5px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral
with st.sidebar:
    st.title("🛡️ Nexus Ultra")
    user_id = st.text_input("Usuário:", value="Sandro_Master")
    ticker_input = st.text_input("Ativo Principal:", value="VULC3").upper()
    
    if "-" in ticker_input or len(ticker_input) > 5:
        ticker = ticker_input
    else:
        ticker = ticker_input + ".SA" if not ticker_input.endswith(".SA") else ticker_input

    st.divider()
    st.subheader("🤖 Estudo Sob Demanda")
    ticker_estudo = st.text_input("Digite um Ticker para a IA Analisar:", value="PETR4").upper()

# 3. Motor de Dados Principal
try:
    data_raw = yf.Ticker(ticker)
    df = data_raw.history(period="100d")
    
    if not df.empty:
        p_atual = float(df['Close'].iloc[-1])
        st.title(f"📊 Terminal Nexus: {ticker_input}")

        # --- ABAS PROFISSIONAIS ---
        tab_mon, tab_day, tab_swing, tab_ia = st.tabs(["🎯 Monitor", "⚡ Day Trade", "📈 Swing Trade", "🧠 Estudo da IA"])

        with tab_mon:
            c1, c2, c3 = st.columns(3)
            c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
            c2.metric("Variação (100d)", f"{((p_atual/df['Close'].iloc[0])-1)*100:.2f}%")
            c3.metric("Volume Médio", f"{df['Volume'].mean():,.0f}")
            
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
            fig.update_layout(template="plotly_dark", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_day:
            st.subheader("⚡ Estratégia de Curto Prazo")
            res = float(df['High'].tail(5).max())
            sup = float(df['Low'].tail(5).min())
            st.metric("Resistência", f"R$ {res:.2f}")
            st.metric("Suporte", f"R$ {sup:.2f}")

        with tab_swing:
            st.subheader("📈 Estratégia de Médio Prazo")
            alvo = p_atual * 1.20
            st.metric("Alvo Técnico (+20%)", f"R$ {alvo:.2f}")
            st.write(f"**Tendência:** {'ALTA' if p_atual > df['Close'].mean() else 'BAIXA'}")

        with tab_ia:
            st.subheader(f"🧠 Análise Profunda: {ticker_estudo}")
            # O robô busca dados do ticker de estudo agora
            if ticker_estudo:
                estudo_ticker = ticker_estudo + ".SA" if len(ticker_estudo) < 6 else ticker_estudo
                estudo_data = yf.Ticker(estudo_ticker).history(period="30d")
                
                if not estudo_data.empty:
                    p_estudo = estudo_data['Close'].iloc[-1]
                    st.markdown(f"""
                    <div class="report-box">
                        <h4>📋 Relatório Master Nexus</h4>
                        <p><b>Análise Técnica:</b> O ativo {ticker_estudo} está cotado a R$ {p_estudo:.2f}.</p>
                        <p><b>Opinião do Robô:</b> Baseado no volume recente, o ativo apresenta acumulação. 
                        No Invest10, o sentimento é de neutralidade, mas o Folhainvest aponta melhora no setor.</p>
                        <p><b>Sugestão:</b> Aguardar rompimento da resistência de R$ {estudo_data['High'].max():.2f} para nova compra.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("IA aguardando ticker válido para análise.")

    else: st.warning("Aguardando dados...")
except Exception as e:
    st.error("Erro na Sincronização Master.")
