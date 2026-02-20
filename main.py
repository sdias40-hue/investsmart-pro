import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Inteligência", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Suporte
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v93(t):
    try:
        t_up = t.upper().strip()
        is_crypto = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_crypto else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return ticker.history(period="60d", interval="1d"), ticker.info, usd_brl
    except: return None, None, 5.60

# --- SIDEBAR: CENTRO DE COMANDO DINÂMICO ---
with st.sidebar:
    st.title("🛡️ Radar Inteligente")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    if 'monitor_v93' not in st.session_state: st.session_state.monitor_v93 = {}
    
    st.divider()
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):").upper().strip()
    
    # Lógica Dinâmica de Campos
    is_cripto_input = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_cripto_input:
        v_inv = st.number_input("Quanto quer investir em REAIS (R$):", min_value=0.0, step=100.0)
        p_compra = st.number_input("Preço da Cripto HOJE (US$):", min_value=0.0)
        p_alvo = st.number_input("Seu Alvo de Venda (US$):", min_value=0.0)
        qtd_acoes = 0
    else:
        p_compra = st.number_input("Preço da Ação HOJE (R$):", min_value=0.0)
        qtd_acoes = st.number_input("Quantidade de Ações compradas:", min_value=0, step=1)
        p_alvo = st.number_input("Seu Alvo de Venda (R$):", min_value=0.0)
        v_inv = p_compra * qtd_acoes

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.monitor_v93[t_in] = {
                    "is_cripto": is_cripto_input,
                    "v_brl": v_inv,
                    "p_in": p_compra,
                    "alvo": p_alvo,
                    "qtd": qtd_acoes
                }
                st.rerun()
    with col2:
        if st.button("🗑️ Limpar Radar"):
            st.session_state.monitor_v93 = {}
            st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Lucro Real")

if not st.session_state.monitor_v93:
    st.info("Radar pronto. Adicione uma Ação ou Cripto para ver o lucro em Reais.")
else:
    for t, cfg in st.session_state.monitor_v93.items():
        h, info, dolar = buscar_v93(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            is_usd = cfg["is_cripto"]
            moeda = "US$" if is_usd else "R$"
            
            # CALCULADORA ADAPTADA
            if is_usd:
                # Cripto: Usa o valor investido em R$ para achar as cotas
                custo_unidade_brl = cfg["p_in"] * dolar
                total_cotas = cfg["v_brl"] / custo_unidade_brl if custo_unidade_brl > 0 else 0
            else:
                # Ação: Usa a quantidade comprada
                total_cotas = cfg["qtd"]
            
            v_investido_brl = cfg["v_brl"] if is_usd else (cfg["p_in"] * cfg["qtd"])
            v_hoje_brl = total_cotas * (p_agora * (dolar if is_usd else 1))
            lucro_brl = v_hoje_brl - v_investido_brl
            
            with st.expander(f"📊 {t} - Monitoramento Ativo", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    st.caption(f"📦 {'Moedas' if is_usd else 'Ações'}: {total_cotas:.6f}")
                with c2:
                    st.metric("Lucro Hoje (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                    st.write(f"💰 Valor Total: R$ {v_hoje_brl:,.2f}")
                with c3:
                    st.subheader("🤖 Mentor Estratégico")
                    if cfg['alvo'] > 0:
                        lucro_alvo = (total_cotas * (cfg['alvo'] * (dolar if is_usd else 1))) - v_investido_brl
                        st.success(f"🎯 Ao bater {moeda} {cfg['alvo']:,.2f}, seu lucro será de **R$ {lucro_alvo:,.2f}**.")
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO!")
                            enviar_alerta(tk, cid, f"🚨 ALERTA: {t} atingiu {moeda}{cfg['alvo']}! Lucro: R$ {lucro_brl:,.2f}")
            
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{t}")
        st.divider()

time.sleep(30)
st.rerun()
