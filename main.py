import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Absolute", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Mensagem e Análise de Day Trade
def enviar_msg(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=20)
def buscar_v160(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- GESTÃO DE MEMÓRIA (image_31e6c5.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: COMANDO DE OPERAÇÕES ---
with st.sidebar:
    st.title("🛡️ Trade Master Pro")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Nova Operação (Day/Swing)")
    
    # FORMULÁRIO COM LIMPEZA REAL (image_31d080.png)
    with st.form("form_trade", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço Compra (R$ ou US$):", min_value=0.0)
        p_alvo = st.number_input("Alvo de Venda (R$ ou US$):", min_value=0.0)
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Quantidade Ações:", min_value=0, step=1)
            v_brl = p_ent * q_a
            
        if st.form_submit_button("🚀 Iniciar Monitoramento"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "p_in": p_ent, "alvo": p_alv, "v_brl": v_brl, "qtd": q_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                }
                st.rerun()

    if st.button("🧹 Limpar Lista de Trades"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Alta Performance")

if not st.session_state.radar:
    st.info("Terminal Pronto. Adicione ativos na lateral para monitorar suportes e resistências.")
else:
    for t, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_v160(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # Cálculo de Suporte e Resistência (Linhas de Kendall - image_242d00.png)
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            
            # Calculadora de Lucro (Ação vs Cripto Corrigida - image_25fe79.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            v_inv_brl = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            lucro_brl = (u_totais * (p_agora * taxa)) - v_inv_brl
            
            with st.expander(f"📊 MONITORANDO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {'US$' if is_c else 'R$'}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t}", key=f"stop_{t}"):
                        del st.session_state.radar[t]
                        st.rerun()
                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                
                with c3:
                    st.subheader("🤖 Mentor Trade Specialist")
                    # Lógica de Alvo Blindada (image_349ddd.png)
                    if cfg['alvo'] > 0:
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO! HORA DE VENDER!")
                            enviar_msg(tk, cid, f"💰 VENDA: {t} atingiu o alvo!")
                        else:
                            st.info(f"💡 Falta {((cfg['alvo']/p_agora)-1)*100:.2f}% para o alvo de {cfg['alvo']:,.2f}.")
                    
                    # Análise de Tendência e Canais
                    if p_agora <= sup * 1.015:
                        st.success("🔥 TRADE DE CONTINUIDADE (Pullback): Preço no Suporte. Hora de comprar!")
                    elif p_agora >= res * 0.985:
                        st.error("⚠️ RESISTÊNCIA DO CANAL: Possível reversão. Hora de realizar lucro!")
                    else:
                        st.write(f"⚖️ Ativo em zona neutra. Suporte: {sup:,.2f} | Resistência: {res:,.2f}")

                # Gráfico Kendall com Suporte e Resistência (image_242d00.png)
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte (Compra)")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência (Venda)")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t}")
        st.divider()

time.sleep(30)
st.rerun()
