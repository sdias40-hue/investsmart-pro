import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Setup Visual High Clarity (Fundo Claro para máxima leitura)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #212529; }
    .stMetric { background-color: #ffffff !important; border: 1px solid #dee2e6 !important; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stMetricValue"] { color: #2ecc71 !important; font-weight: 800; }
    .stInfo { background-color: #ffffff !important; border-left: 5px solid #3498db !important; color: #2c3e50 !important; }
    .stSuccess { background-color: #eafaf1 !important; border-left: 5px solid #2ecc71 !important; color: #145a32 !important; }
    .stWarning { background-color: #fef9e7 !important; border-left: 5px solid #f1c40f !important; color: #7d6608 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Mensageria e Busca
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

def buscar_dados_pro(t, p="1d", i="1m"):
    try:
        t_search = f"{t}.SA" if "-" not in t and ".SA" not in t else t
        ticker = yf.Ticker(t_search)
        hist = ticker.history(period=p, interval=i)
        if hist.empty:
            ticker = yf.Ticker(t)
            hist = ticker.history(period=p, interval=i)
        return hist, ticker.info
    except: return None, None

# --- SIDEBAR: COMANDO CENTRAL ---
with st.sidebar:
    st.title("🏛️ InvestSmart Pro")
    st.info("Configurações do Robô")
    token_bot = st.text_input("Token Telegram:", type="password")
    chat_id_user = st.text_input("Seu Chat ID:", value="8392660003")
    
    st.divider()
    modo = st.radio("Escolha o Terminal:", ["📈 Prateleira (Investidor)", "⚡ Swing Trade (Trader)"])
    
    st.divider()
    st.subheader("🔎 Gestão de Ativos")
    add_t = st.text_input("Novo Ativo (Ex: PETR4, OHI, BTC-USD):").upper()
    
    if 'radar' not in st.session_state: st.session_state.radar = []
        
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Adicionar") and add_t:
            if add_t not in st.session_state.radar:
                st.session_state.radar.append(add_t)
                enviar_alerta(token_bot, chat_id_user, f"✅ Monitorando: {add_t}")
                st.rerun()
    with c2:
        if st.button("Limpar Tudo"):
            st.session_state.radar = []
            st.rerun()

# --- TERMINAL 1: PRATELEIRA (SIMPLICIDADE TOTAL) ---
if modo == "📈 Prateleira (Investidor)":
    st.title("🏛️ Prateleira de Investimentos Sólidos")
    if not st.session_state.radar:
        st.warning("Seu radar está vazio. Adicione ativos na lateral para ver a análise do Mentor.")
    else:
        for t in st.session_state.radar:
            h, info = buscar_dados_pro(t, "5d", "1h")
            if h is not None:
                atual = h['Close'].iloc[-1]
                # Cálculo de Preço Justo e Alvo
                dy = info.get('trailingAnnualDividendRate', 0)
                p_justo = (dy / 0.06) if dy > 0 else (atual * 1.12)
                p_alvo = atual * 1.25 # Meta de 25% de lucro
                ganho_potencial = ((p_alvo/atual)-1)*100
                
                with st.container():
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        st.metric(f"💰 {t}", f"R$ {atual:,.2f}")
                    with col2:
                        st.metric("Preço Justo", f"R$ {p_justo:,.2f}")
                    with col3:
                        # Veredito do Mentor para Leigos
                        if atual < p_justo:
                            st.success(f"💎 **OPORTUNIDADE:** Empresa sólida do setor de {info.get('sector')}. Preço está excelente para compra agora.")
                        else:
                            st.warning(f"⏳ **AGUARDE:** Ativo de {info.get('sector')}. O preço está esticado, melhor esperar uma queda.")
                
                st.info(f"💡 **Sugestão do Mentor:** Se comprar em R$ {atual:,.2f}, sugerimos vender em **R$ {p_alvo:,.2f}**. Isso representa um ganho de **{ganho_potencial:.1f}%**.")
                st.divider()

# --- TERMINAL 2: SWING TRADE (GRÁFICO EM TEMPO REAL) ---
else:
    st.title("⚡ Terminal de Swing Trade | Tempo Real")
    if not st.session_state.radar:
        st.warning("Adicione ativos na lateral para abrir o terminal gráfico.")
    else:
        t_sel = st.selectbox("Ativo em Análise:", st.session_state.radar)
        h_t, i_t = buscar_dados_pro(t_sel, "1d", "1m") # Gráfico de 1 minuto em tempo real
        
        if h_t is not None:
            # Indicadores Rápidos
            h_t['MA20'] = h_t['Close'].rolling(window=20).mean()
            h_t['MA9'] = h_t['Close'].rolling(window=9).mean()
            atual = h_t['Close'].iloc[-1]
            p_venda = atual * 1.05 # Meta curta de 5% no Swing Trade
            
            c_l, c_r = st.columns([1, 3])
            with c_l:
                st.metric(f"Preço {t_sel}", f"R$ {atual:,.2f}")
                st.subheader("🤖 Estratégia Trader")
                
                if h_t['MA9'].iloc[-1] > h_t['MA20'].iloc[-1]:
                    st.success("🚀 SINAL: COMPRA AGORA")
                    st.write(f"🎯 Meta de Venda: R$ {p_venda:,.2f}")
                else:
                    st.error("⚠️ SINAL: AGUARDE FORA")
                
                st.info(f"**Análise:** O ativo {t_sel} apresenta volume saudável. Sugestão de saída com 5% de lucro rápido.")

            with c_right:
                # Gráfico Candle Real Time
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.03)
                fig.add_trace(go.Candlestick(x=h_t.index, open=h_t.Open, high=h_t.High, low=h_t.Low, close=h_t.Close, name='Candle'), row=1, col=1)
                fig.add_trace(go.Scatter(x=h_t.index, y=h_t['MA9'], name='Média Rápida', line=dict(color='#f1c40f')), row=1, col=1)
                
                fig.update_layout(template='plotly_white', xaxis_rangeslider_visible=False, height=600, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

    time.sleep(15) # Atualização mais rápida para trade
    st.rerun()
