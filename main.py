import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Layout de Alta Performance
st.set_page_config(page_title="InvestSmart Pro | Multi-Ativos", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff !important; border-radius: 12px; padding: 15px; border: 1px solid #dee2e6; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stExpander { background-color: #ffffff !important; border-radius: 12px !important; border: 1px solid #dee2e6 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Funções de Busca e Alerta
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v87(t):
    try:
        # Correção automática para Cripto e Ações (image_e1717f.jpg)
        is_crypto = t.upper() in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t.upper()}-USD" if is_crypto else (f"{t.upper()}.SA" if "." not in t else t.upper())
        ticker = yf.Ticker(search)
        return ticker.history(period="60d", interval="1d"), ticker.info
    except: return None, None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Radar Estratégico")
    token = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("ID Telegram:", value="8392660003")
    
    if 'lista_monitor' not in st.session_state: st.session_state.lista_monitor = {}
    
    st.divider()
    t_input = st.text_input("Adicionar Ativo:").upper().strip()
    p_in = st.number_input("Preço de Compra (Opcional):", min_value=0.0, step=0.01)
    p_out = st.number_input("Preço Alvo (Venda):", min_value=0.0, step=0.01)
    
    if st.button("🚀 Monitorar Ativo"):
        if t_input:
            st.session_state.lista_monitor[t_input] = {"compra": p_in, "alvo": p_out}
            st.rerun()

    if st.button("🗑️ Limpar Painel"):
        st.session_state.lista_monitor = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Dashboard em Tempo Real")

if not st.session_state.lista_monitor:
    st.info("O painel está limpo. Adicione a VULC3 e o BTC para ver a análise simultânea.")
else:
    # Exibe cada ativo em um quadro independente
    for t, config in st.session_state.lista_monitor.items():
        h, info = buscar_v87(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            ma9 = h['Close'].rolling(9).mean().iloc[-1]
            ma20 = h['Close'].rolling(20).mean().iloc[-1]
            
            with st.expander(f"📈 ANALISANDO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                
                with c1:
                    var_dia = ((p_agora / h['Open'].iloc[-1]) - 1) * 100
                    st.metric("Preço Atual", f"{p_agora:,.2f}", f"{var_dia:.2f}%")
                    if config['compra'] > 0:
                        lucro = ((p_agora / config['compra']) - 1) * 100
                        st.write(f"💰 Lucro: {lucro:.2f}%")
                
                with c2:
                    if config['alvo'] > 0:
                        st.metric("Alvo de Venda", f"{config['alvo']:,.2f}")
                        if p_agora >= config['alvo']:
                            st.success("🚨 ALVO ATINGIDO!")
                            enviar_alerta(token, cid, f"✅ HORA DE VENDER: {t} atingiu {p_agora:,.2f}!")
                    else:
                        st.write("🔍 Apenas observando tendência.")

                with c3:
                    # Análise de Projeção Kendall (image_8aad4d.png)
                    if p_agora > ma9 and ma9 > ma20:
                        st.success(f"🚀 PROJEÇÃO: Grande possibilidade de subir! O padrão de Kendall indica força compradora em {t}.")
                    else:
                        st.info(f"⚖️ TENDÊNCIA: {t} em zona de consolidação. Aguarde sinal claro de Kendall.")

                # Gráfico de Candles para cada ativo
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close, name='Candle')])
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{t}")
        else:
            st.error(f"Erro ao carregar {t}. Verifique o código do ativo.")

# Atualização Online
time.sleep(30)
st.rerun()
