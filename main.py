import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Configuração de Visibilidade Total (Padronização de Cores)
st.set_page_config(page_title="Nexus Ultra | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Fundo Preto Absoluto */
    .main { background-color: #000000; color: #ffffff; }
    
    /* Fontes Padronizadas: Tudo Branco ou Azul Neon para não apagar */
    h1, h2, h3, h4, p, span, label, .stMarkdown { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif;
    }
    
    .neon-blue { color: #00d4ff !important; font-weight: bold; }

    /* Métricas com Contorno Azul Neon */
    .stMetric { 
        background-color: #0a0a0a !important; 
        border: 2px solid #00d4ff !important; 
        border-radius: 12px; 
        padding: 20px; 
    }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #00d4ff !important; font-weight: bold !important; }

    /* Card de Relatório da IA - Blindado */
    .ia-card { 
        background-color: #0e1117; 
        border: 1px solid #ffffff; 
        border-left: 10px solid #00d4ff; 
        padding: 25px; 
        border-radius: 10px; 
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Comando Lateral
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Ultra</h2>", unsafe_allow_html=True)
    user_id = st.text_input("Usuário:", value="Sandro_Master")
    # Ativo do Gráfico Principal
    ticker_mon = st.text_input("Monitorar Gráfico:", value="VULC3").upper()
    st.divider()
    st.info("Status: Sistema Online (Nuvem)")

# 3. Motor de Dados Estabilizado (Monitor)
ticker_final = ticker_mon + ".SA" if len(ticker_mon) < 6 and "." not in ticker_mon else ticker_mon

try:
    # Busca leve para o gráfico não travar
    data = yf.download(ticker_final, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>🚀 Terminal Nexus: <span class='neon-blue'>{ticker_mon}</span></h1>", unsafe_allow_html=True)

        # --- SISTEMA DE ABAS ---
        tab_mon, tab_day, tab_swing, tab_ia = st.tabs(["🎯 Monitor", "⚡ Day Trade", "📈 Swing Trade", "🧠 Estudo da IA"])

        with tab_mon:
            c1, c2, c3 = st.columns(3)
            c1.metric("Preço Agora", f"R$ {p_atual:,.2f}")
            c2.metric("Variação (60d)", f"{((p_atual/data['Close'].iloc[0])-1)*100:.2f}%")
            c3.metric("Volume Médio", f"{data['Volume'].mean():,.0f}")
            
            fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
            fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_day:
            st.markdown("<h3 class='neon-blue'>⚡ Radar Day Trade</h3>", unsafe_allow_html=True)
            res = float(data['High'].tail(5).max())
            sup = float(data['Low'].tail(5).min())
            st.metric("Resistência (Topo)", f"R$ {res:.2f}")
            st.metric("Suporte (Fundo)", f"R$ {sup:.2f}")

        with tab_swing:
            st.markdown("<h3 class='neon-blue'>📈 Radar Swing Trade</h3>", unsafe_allow_html=True)
            st.metric("Alvo Técnico (+20%)", f"R$ {p_atual * 1.20:.2f}")
            st.write(f"**Tendência do Ativo:** {'ALTA' if p_atual > data['Close'].mean() else 'BAIXA'}")

        with tab_ia:
            st.markdown("<h3 class='neon-blue'>🧠 Estudo Independente (IA Nexus)</h3>", unsafe_allow_html=True)
            # Campo separado para o robô não misturar as informações
            ticker_ia = st.text_input("Digite o Ticker para o Robô Pensar (ex: S2WA34, PETR4):", key="input_ia").upper()
            
            if ticker_ia:
                t_ia_final = ticker_ia + ".SA" if len(ticker_ia) < 6 and "." not in ticker_ia else ticker_ia
                # Busca rápida apenas do último dado para o relatório
                ia_data = yf.Ticker(t_ia_final).history(period="5d")
                
                if not ia_data.empty:
                    p_ia = ia_data['Close'].iloc[-1]
                    st.markdown(f"""
                    <div class='ia-card'>
                        <h4 class='neon-blue'>📋 Relatório de Estudo: {ticker_ia}</h4>
                        <p><b>Análise de Mercado:</b> O ativo está cotado em R$ {p_ia:.2f}.</p>
                        <p><b>Opinião do Robô:</b> Baseado no histórico de 5 dias, o ativo apresenta suporte em R$ {ia_data['Low'].min():.2f}. 
                        Radar Invest10 e Folhainvest sugerem entrada se houver rompimento de volume.</p>
                        <p><b>Conclusão:</b> Estratégia Master recomenda monitorar o suporte antes de novos aportes.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Não consegui ler os dados de {ticker_ia}. Verifique o código.")

    else: st.warning("Aguardando sincronização com a Nuvem...")
except Exception as e:
    st.error("Erro Master: Conexão temporária indisponível.")
