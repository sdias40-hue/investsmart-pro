import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

# 1. Setup Visual High Clarity
st.set_page_config(page_title="InvestSmart Pro | Monitoramento Ativo", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff !important; border-radius: 12px; padding: 15px; border: 1px solid #dee2e6; }
    .stInfo { border-left: 5px solid #007bff !important; }
    .stSuccess { border-left: 5px solid #28a745 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Motor de Alerta e Analise Técnica
def enviar_alerta_telegram(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30) # Atualização rápida para ficar "Online"
def buscar_dados_v86(t):
    try:
        search = f"{t.upper()}-USD" if t.upper() in ["BTC", "XRP", "ETH"] else (f"{t.upper()}.SA" if ".SA" not in t.upper() else t.upper())
        ticker = yf.Ticker(search)
        return ticker.history(period="60d", interval="1d"), ticker.info
    except: return None, None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Centro de Alertas")
    token_bot = st.text_input("Token Telegram:", type="password")
    chat_id_user = st.text_input("ID Telegram:", value="8392660003")
    
    st.divider()
    # Radar Único de Monitoramento Ativo
    if 'monitor' not in st.session_state: st.session_state.monitor = {}
    
    st.subheader("🚀 Monitorar Nova Compra")
    new_t = st.text_input("Ticker (Ex: VULC3, BTC):").upper()
    p_compra = st.number_input("Preço que pagou:", min_value=0.0, step=0.01)
    p_alvo = st.number_input("Preço de Venda (Alvo):", min_value=0.0, step=0.01)
    
    if st.button("Ativar Vigia"):
        if new_t:
            st.session_state.monitor[new_t] = {"compra": p_compra, "alvo": p_alvo}
            st.success(f"Vigia ativado para {new_t}")
            st.rerun()

    if st.button("Limpar Todos os Alertas"):
        st.session_state.monitor = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Online")

if not st.session_state.monitor:
    st.info("Nenhuma ação em monitoramento. Use a barra lateral para adicionar ativos como a VULC3.")
else:
    for t, dados in st.session_state.monitor.items():
        h, info = buscar_dados_v86(t)
        if h is not None and not h.empty:
            p_atual = h['Close'].iloc[-1]
            lucro_bruto = ((p_atual / dados['compra']) - 1) * 100 if dados['compra'] > 0 else 0
            
            # Layout de Monitoramento
            with st.expander(f"📊 MONITORANDO: {t} (Lucro: {lucro_bruto:.2f}%)", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    st.metric("Preço Atual", f"R$ {p_atual:,.2f}", f"{lucro_bruto:.2f}%")
                    st.write(f"📉 Compra: R$ {dados['compra']:.2f}")
                
                with col2:
                    st.metric("Alvo de Venda", f"R$ {dados['alvo']:.2f}")
                    distancia = ((dados['alvo'] / p_atual) - 1) * 100
                    st.write(f"🎯 Faltam: {distancia:.2f}%")

                with col3:
                    # ANALISE DE PROJEÇÃO (KANDALL)
                    ma9 = h['Close'].rolling(9).mean().iloc[-1]
                    ma20 = h['Close'].rolling(20).mean().iloc[-1]
                    
                    if p_atual >= dados['alvo']:
                        st.success(f"🚨 HORA DE VENDER! {t} atingiu R$ {p_atual:.2f}")
                        enviar_alerta_telegram(token_bot, chat_id_user, f"💰 ALERTA DE LUCRO: {t} atingiu o alvo de R$ {dados['alvo']}. Preço atual: R$ {p_atual}")
                    
                    elif p_atual > ma9 and ma9 > ma20:
                        st.success(f"🔥 PROJEÇÃO DE SUBIDA: {t} em forte tendência de alta no gráfico de Kendall.")
                        # Envia apenas um alerta por sessão para não poluir
                        if "alerta_enviado_"+t not in st.session_state:
                            enviar_alerta_telegram(token_bot, chat_id_user, f"🚀 PROJEÇÃO: {t} analisada pelo InvestSmart Pro com grande chance de subida!")
                            st.session_state["alerta_enviado_"+t] = True
                    else:
                        st.info("⚡ Monitorando... Aguardando sinal de força compradora.")

                # Gráfico Online Independente
                fig = make_subplots(rows=1, cols=1)
                fig.add_trace(go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close, name='Candle'))
                fig.add_hline(y=dados['alvo'], line_dash="dot", line_color="green", annotation_text="ALVO DE VENDA")
                fig.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

# Loop de atualização "sempre online" (refresh a cada 30 segundos)
time.sleep(30)
st.rerun()
