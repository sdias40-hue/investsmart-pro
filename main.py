import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup de Interface Profissional
st.set_page_config(page_title="InvestSmart Pro | Smart Filter", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Inteligência e Mensageria
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=20)
def buscar_dados(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- MEMÓRIA DO SISTEMA ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO INTELIGENTE ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Consulta ou Trade")
    
    with st.form("form_comando", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço Compra (Opcional):", min_value=0.0)
        p_alv = st.number_input("Alvo Venda (Opcional):", min_value=0.0)
        
        # Lógica de seleção
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            invest = st.number_input("Valor Investido (R$):", min_value=0.0)
            qtd_a = 0
        else:
            qtd_a = st.number_input("Quantidade Ações:", min_value=0, step=1)
            invest = p_ent * qtd_a
            
        if st.form_submit_button("🚀 Executar"):
            if t_in:
                # SEGREDO DA LÓGICA: Se preencheu valores, vai para o Radar (Lista). Se não, é só consulta.
                if p_ent > 0 or p_alv > 0 or invest > 0:
                    st.session_state.radar[t_in] = {
                        "p_in": p_ent, "alvo": p_alv, "v_brl": invest, "qtd": qtd_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                    }
                    st.session_state.consulta = None # Limpa consulta se iniciou trade
                else:
                    st.session_state.consulta = t_in # Define apenas como consulta rápida
                st.rerun()

    if st.button("🗑️ Limpar Monitoramento Ativo"):
        st.session_state.radar = {}
        st.session_state.consulta = None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Trade Specialist")

# SEÇÃO 1: CONSULTA RÁPIDA (Não entra na lista fixa)
if st.session_state.consulta:
    t = st.session_state.consulta
    h, info, dolar, is_c = buscar_dados(t)
    if h is not None and not h.empty:
        st.subheader(f"🔍 Consulta Rápida: {t}")
        p_agora = h['Close'].iloc[-1]
        st.metric(f"Preço Atual ({'US$' if is_c else 'R$'})", f"{p_agora:,.2f}")
        
        # Gráfico de Consulta
        fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
        fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO (Apenas quem tem dados preenchidos)
if not st.session_state.radar:
    st.info("Nenhuma operação ativa no radar. Preencha os valores na lateral para monitorar.")
else:
    st.subheader("📋 Mensagens e Operações Ativas")
    for t_at, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_dados(t_at)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # Cálculo de Suporte e Resistência (Linhas de Kendall)
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            
            # Calculadora de Lucro Real
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            v_atual_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_atual_brl - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📈 TRADE ATIVO: {t_at}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric("Preço Agora", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}")
                with c3:
                    st.subheader("🤖 Mentor Day Trade")
                    # Lógica de Alvo Corrigida (Ex: 67k vs 90k)
                    if cfg['alvo'] > 0:
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 META ATINGIDA!")
                            enviar_alerta(tk, cid, f"💰 ALVO ATINGIDO: {t_at} em {p_agora:,.2f}")
                        else:
                            st.info(f"Falta {((cfg['alvo']/p_agora)-1)*100:.2f}% para o alvo de {cfg['alvo']:,.2f}.")
                    
                    # Sinais de Trade (Pullback e Rompimento)
                    if p_agora <= sup * 1.015:
                        st.success("🔥 SINAL DE COMPRA: Pullback no Suporte!")
                    elif p_agora >= res * 0.985:
                        st.error("⚠️ SINAL DE VENDA: Testando Resistência!")

                # Gráfico com Linhas de Tendência
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")
        st.divider()

time.sleep(30)
st.rerun()
