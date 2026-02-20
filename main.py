import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface Profissional (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Enterprise", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Suporte Blindadas
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_dados_v100(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        # Busca Global para Cripto e B3 para Ações
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), usd_brl, is_c
    except: return None, 5.65, False

# --- INICIALIZAÇÃO DE ESTADOS (Prevenção de image_267b37.jpg) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'limpar_acionado' not in st.session_state: st.session_state.limpar_acionado = False

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Adicionar Ativo")
    
    # Inputs sem chaves fixas para evitar travamento de API
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):").upper().strip()
    is_cripto_in = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_cripto_in:
        v_inv = st.number_input("Investir em R$:", min_value=0.0, step=100.0)
        p_ent = st.number_input("Preço Compra (US$):", min_value=0.0)
        p_alv = st.number_input("Alvo Venda (US$):", min_value=0.0)
        qtd_a = 0
    else:
        p_ent = st.number_input("Preço Compra (R$):", min_value=0.0)
        qtd_a = st.number_input("Qtd Ações:", min_value=0, step=1)
        p_alv = st.number_input("Alvo Venda (R$):", min_value=0.0)
        v_inv = p_ent * qtd_a

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "is_c": is_cripto_in, "v_brl": v_inv, "p_in": p_ent, "alvo": p_alv, "qtd": qtd_a
                }
                st.rerun()
    with c2:
        if st.button("🧹 Limpar Campos"):
            # Reset Seguro: Recarrega a aplicação sem causar image_267b37.jpg
            st.rerun()

    st.divider()
    st.subheader("📋 Lista Ativa")
    for t_l in list(st.session_state.radar.keys()):
        st.write(f"• {t_l}")

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Multi-Ativos")

if not st.session_state.radar:
    st.info("Radar pronto. Adicione seus ativos na lateral para iniciar o vigia.")
else:
    for t_at in list(st.session_state.radar.keys()):
        cfg = st.session_state.radar[t_at]
        h, dolar, is_c = buscar_dados_v100(t_at)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            moeda = "US$" if is_c else "R$"
            
            # Calculadora Precisa (image_25fe79.png)
            taxa = dolar if is_c else 1.0
            total_u = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c and cfg["p_in"] > 0 else cfg["qtd"]
            v_inv_brl = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            v_hoje_brl = total_u * (p_agora * taxa)
            lucro_brl = v_hoje_brl - v_inv_brl
            
            with st.expander(f"📊 MONITORANDO: {t_at}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    if st.button(f"Parar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with col2:
                    st.metric("Lucro Hoje (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with col3:
                    st.subheader("🤖 Mentor Estratégico")
                    if cfg['alvo'] > 0:
                        v_alvo_brl = total_u * (cfg['alvo'] * taxa)
                        st.success(f"🎯 Alvo {moeda} {cfg['alvo']:,.2f} = Lucro de **R$ {v_alvo_brl - v_inv_brl:,.2f}**")
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO!")
                            enviar_alerta(tk, cid, f"💰 VENDA: {t_at} atingiu o alvo! Lucro: R$ {lucro_brl:,.2f}")

                # Gráfico com proteção contra erro de carregamento (image_267b17.png)
                try:
                    fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                    fig.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{t_at}")
                except:
                    st.warning("Aguardando estabilização dos dados...")
        st.divider()

time.sleep(30)
st.rerun()
