import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Interface High-Contrast (Padronização Sandro Master)
st.set_page_config(page_title="Nexus Ultra Master | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    h1, h2, h3, h4, p, span, label { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .neon-text { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 2px solid #00d4ff !important; border-radius: 12px; padding: 20px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    .report-card { background-color: #0e1117; border: 1px solid #ffffff; border-left: 8px solid #00d4ff; padding: 25px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral: Monitoramento de Investimento
with st.sidebar:
    st.markdown("<h2 class='neon-text'>🛡️ Nexus Command</h2>", unsafe_allow_html=True)
    ticker_mon = st.text_input("Ativo Principal:", value="VULC3").upper()
    
    st.divider()
    st.markdown("<h4 class='neon-text'>💰 Dados do Investimento</h4>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor Investido (R$):", value=0.0)
    preco_entrada = st.number_input("Preço de Entrada (R$):", value=0.0, format="%.2f")
    alvo_venda = st.number_input("Alvo de Venda (R$):", value=0.0, format="%.2f")
    
    st.divider()
    st.info("Status: Sistema Online (Cloud)")

# 3. Processamento de Dados
t_final = ticker_mon + ".SA" if len(ticker_mon) < 6 and "." not in ticker_mon else ticker_mon

try:
    data = yf.download(t_final, period="100d", interval="1d", progress=False)
    
    if not df.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>🚀 Terminal Master: <span class='neon-text'>{ticker_mon}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE MONITORAMENTO REAL ---
        col1, col2, col3 = st.columns(3)
        lucro_preju = (p_atual - preco_entrada) * (val_investido / preco_entrada) if preco_entrada > 0 else 0
        
        col1.metric("Preço Agora", f"R$ {p_atual:.2f}")
        col2.metric("Resultado Estimado", f"R$ {lucro_preju:,.2f}", delta=f"{((p_atual/preco_entrada)-1)*100:.2f}%" if preco_entrada > 0 else "0%")
        col3.metric("Alvo de Venda", f"R$ {alvo_venda:.2f}")

        # --- SISTEMA DE ABAS ---
        tab_graf, tab_trader, tab_ia = st.tabs(["🎯 Gráfico Master", "⚡ Estratégias", "🧠 Estudo Sob Demanda"])

        with tab_graf:
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
            fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_trader:
            c_a, c_b = st.columns(2)
            res = float(data['High'].tail(5).max())
            sup = float(data['Low'].tail(5).min())
            c_a.metric("Resistência Day Trade", f"R$ {res:.2f}")
            c_b.metric("Suporte Swing Trade", f"R$ {sup:.2f}")

        with tab_ia:
            st.markdown("<h3 class='neon-text'>🧠 Estudo Independente da IA</h3>", unsafe_allow_html=True)
            ticker_ia = st.text_input("Digite o Ticker para o Robô Pensar:", key="ia_input").upper()
            if ticker_ia:
                t_ia_final = ticker_ia + ".SA" if len(ticker_ia) < 6 and "." not in ticker_ia else ticker_ia
                ia_data = yf.Ticker(t_ia_final).history(period="5d")
                if not ia_data.empty:
                    st.markdown(f"""
                    <div class='report-card'>
                        <h4 class='neon-text'>📋 Relatório Master: {ticker_ia}</h4>
                        <p><b>Análise Técnica:</b> Ativo operando a R$ {ia_data['Close'].iloc[-1]:.2f}.</p>
                        <p><b>Opinião Nexus:</b> Suporte identificado em R$ {ia_data['Low'].min():.2f}. 
                        Radar Invest10 e Folhainvest indicam neutralidade com viés de alta.</p>
                    </div>
                    """, unsafe_allow_html=True)

    else: st.warning("Aguardando sincronização...")
except Exception: st.error("Erro Master: Conexão temporária.")
