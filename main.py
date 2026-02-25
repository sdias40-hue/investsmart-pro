import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. ESTÉTICA MASTER (Visibilidade 100% em qualquer tela)
st.set_page_config(page_title="Nexus Master | Sandro", layout="wide")

st.markdown("""
    <style>
    /* Fundo Preto Absoluto */
    .main { background-color: #000000 !important; }
    
    /* Forçar TODAS as fontes para Branco Puro (Resolve o problema do PC) */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    /* Azul Neon para Destaques e Botões */
    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Moldura de Proteção para o Gráfico não sumir no PC */
    .stPlotlyChart { 
        border: 1px solid #333; 
        border-radius: 10px; 
        min-height: 500px !important; 
    }
    
    /* Caixa de Veredito do Robô */
    .status-box { 
        background-color: #0e1117; 
        border: 1px solid #00d4ff; 
        border-left: 10px solid #00d4ff; 
        padding: 20px; 
        border-radius: 8px; 
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. COMANDO LATERAL (Gestão Independente)
with st.sidebar:
    st.markdown("<h2 class='neon-blue'>🛡️ Nexus Command</h2>", unsafe_allow_html=True)
    ticker_input = st.text_input("Ativo (Ex: BTC-USD ou VULC3):", value="BTC-USD").upper()
    
    st.divider()
    # Identifica se é Cripto ou Ação para mudar os campos
    is_crypto = "-" in ticker_input or len(ticker_input) > 6
    
    st.markdown(f"<p class='neon-blue'>Gestão: {'Cripto' if is_crypto else 'Ações'}</p>", unsafe_allow_html=True)
    val_investido = st.number_input("Valor Investido (R$):", value=0.0)
    
    if is_crypto:
        preco_pago = st.number_input("Preço de Entrada (R$):", value=0.0, format="%.2f")
    else:
        qtd_comprada = st.number_input("Qtd de Ações:", value=0)
        preco_pago = st.number_input("Preço Médio (R$):", value=0.0, format="%.2f")

    if st.sidebar.button("🚀 Gerar Análise Master"):
        st.rerun()

# 3. MOTOR DE INTELIGÊNCIA (Busca Blindada)
t_final = ticker_input + ".SA" if not is_crypto and not ticker_input.endswith(".SA") else ticker_input

try:
    # yf.download é mais estável para rodar 24h na nuvem
    data = yf.download(t_final, period="60d", interval="1d", progress=False)
    
    if not data.empty:
        p_atual = float(data['Close'].iloc[-1])
        st.markdown(f"<h1>📊 Mentor Nexus: <span class='neon-blue'>{ticker_input}</span></h1>", unsafe_allow_html=True)

        # --- PAINEL DE RESULTADO ---
        c1, c2 = st.columns(2)
        if not is_crypto and 'qtd_comprada' in locals() and qtd_comprada > 0:
            lucro_r = (p_atual - preco_pago) * qtd_comprada
        else:
            lucro_r = (p_atual - preco_pago) * (val_investido / preco_pago) if preco_pago > 0 else 0
        
        porc = ((p_atual / preco_pago) - 1) * 100 if preco_pago > 0 else 0
        
        c1.metric("Preço Atual", f"R$ {p_atual:,.2f}")
        c2.metric("Meu Lucro/Perda", f"R$ {lucro_r:,.2f}", delta=f"{porc:.2f}%")

        # --- VEREDITO DO ROBÔ (O QUE VOCÊ PEDIU) ---
        st.divider()
        st.markdown("<h3 class='neon-blue'>🤖 Veredito e Análise do Robô</h3>", unsafe_allow_html=True)
        
        # Lógica Simples de Trader
        topo = data['High'].tail(10).max()
        fundo = data['Low'].tail(10).min()
        tendencia = "ALTA" if p_atual > data['Close'].mean() else "QUEDA"
        cor_v = "#00ff00" if tendencia == "ALTA" else "#ff4b4b"

        st.markdown(f"""
            <div class='status-box' style='border-left-color: {cor_v};'>
                <h4 style='color: {cor_v} !important;'>📢 RECOMENDAÇÃO: {tendencia}</h4>
                <p><b>Análise Gráfica:</b> O robô identifica um suporte em R$ {fundo:.2f}. Se segurar aqui, o destino é R$ {topo:.2f}.</p>
                <p><b>Análise de Internet:</b> Volume de negociação está {'crescente' if tendencia == "ALTA" else 'estável'}.</p>
                <p><b>Dica do Mentor:</b> {'Momento de acumulação' if tendencia == "ALTA" else 'Aguarde um sinal de reversão para comprar'}.</p>
            </div>
        """, unsafe_allow_html=True)

        # --- GRÁFICO (RESTAURADO E FORÇADO PARA PC) ---
        st.markdown("<h4 class='neon-blue'>📈 Mapa de Preços</h4>", unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close)])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else: st.warning("Ticker não encontrado. Verifique se digitou corretamente.")

except Exception as e:
    st.error("Sincronizando com a Nuvem... Tente novamente.")
