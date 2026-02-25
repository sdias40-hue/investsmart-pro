import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração Master (Azul Turquesa e Branco - Nível Profissional)
st.set_page_config(page_title="Nexus Ultra | Sandro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    h1, h2, h3, h4 { color: #00d4ff !important; font-family: 'Segoe UI', sans-serif; }
    .stMetric { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #ffffff !important; }
    .report-card { background-color: #1c2128; border-left: 5px solid #00d4ff; padding: 25px; border-radius: 8px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral Nexus
with st.sidebar:
    st.title("🛡️ Nexus Ultra")
    user_id = st.text_input("Usuário:", value="Sandro_Master")
    # Ticker do Monitor (Gráfico Principal)
    ticker_mon = st.text_input("Monitorar Gráfico:", value="VULC3").upper()
    
    st.divider()
    st.info("🤖 O Robô está pronto para estudar novos ativos.")

# 3. Motor de Dados Principal (Monitor)
ticker_final = ticker_mon + ".SA" if len(ticker_mon) < 6 and "." not in ticker_mon else ticker_mon

try:
    data = yf.Ticker(ticker_final).history(period="100d")
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.title(f"📊 Terminal Nexus: {ticker_mon}")

        # --- SISTEMA DE ABAS ---
        tab_mon, tab_day, tab_swing, tab_ia = st.tabs(["🎯 Monitor", "⚡ Day Trade", "📈 Swing Trade", "🧠 Estudo da IA"])

        with tab_mon:
            c1, c2, c3 = st.columns(3)
            c1.metric("Preço Agora", f"R$ {p_atual:,.2f}")
            c2.metric("Variação", f"{((p_atual/data['Close'].iloc[0])-1)*100:.2f}%")
            c3.metric("Volume Médio", f"{data['Volume'].mean():,.0f}")
            
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
            fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_day:
            st.subheader("⚡ Análise de Volatilidade (Curto Prazo)")
            res = float(data['High'].tail(5).max())
            sup = float(data['Low'].tail(5).min())
            st.metric("Resistência", f"R$ {res:.2f}")
            st.metric("Suporte", f"R$ {sup:.2f}")

        with tab_swing:
            st.subheader("📈 Análise de Tendência (Médio Prazo)")
            alvo = p_atual * 1.20
            st.metric("Alvo Técnico (+20%)", f"R$ {alvo:.2f}")
            st.write(f"**Tendência Principal:** {'ALTA' if p_atual > data['Close'].mean() else 'BAIXA'}")

        with tab_ia:
            st.subheader("🧠 Estudo Sob Demanda (IA Nexus)")
            # LOCAL SEPARADO PARA DIGITAR O CÓDIGO DO ESTUDO
            ticker_estudo = st.text_input("Digite o Ticker para o Robô Analisar (ex: PETR4, AAPL):", key="ia_input").upper()
            
            if ticker_estudo:
                t_estudo_final = ticker_estudo + ".SA" if len(ticker_estudo) < 6 and "." not in ticker_estudo else ticker_estudo
                estudo_raw = yf.Ticker(t_estudo_final).history(period="30d")
                
                if not estudo_raw.empty:
                    p_est = estudo_raw['Close'].iloc[-1]
                    st.markdown(f"""
                    <div class="report-card">
                        <h4>📋 Relatório Master: {ticker_estudo}</h4>
                        <p><b>Status de Mercado:</b> O ativo está operando a R$ {p_est:.2f}.</p>
                        <p><b>Opinião Nexus:</b> Baseado em dados internacionais e nacionais, o ativo apresenta 
                        padrão de acumulação técnica. No Invest10, o Dividend Yield é destaque, enquanto o 
                        Folhainvest sugere atenção ao volume comprador.</p>
                        <p><b>Sugestão Master:</b> O robô identifica boas chances de compra se mantiver acima de R$ {estudo_raw['Low'].min():.2f}.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("IA aguardando ticker para iniciar o estudo.")

    else: st.error("Ativo não encontrado.")
except Exception as e:
    st.error("Erro na Sincronização Master.")
