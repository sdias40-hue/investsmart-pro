import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Trader", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca e Mensageria
def enviar_telegram(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=20)
def buscar_v190(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- GESTÃO DE MEMÓRIA (image_3172e1.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO DE OPERAÇÕES ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Consulta ou Monitorar")
    
    # RESOLUÇÃO DO ERRO DE LIMPEZA (image_35735a.png): Uso de formulário nativo
    with st.form("trade_form", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço de Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo de Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Quantidade Ações:", min_value=0, step=1)
            v_brl = p_ent * q_a
            
        submitted = st.form_submit_button("🚀 Executar")
        
        if submitted and t_in:
            # LÓGICA SMART: Se preencher valores, entra na lista. Se não, é só consulta rápida.
            if p_ent > 0 or p_alv > 0:
                st.session_state.radar[t_in] = {
                    "p_in": p_ent, "alvo": p_alv, "v_brl": v_brl, "qtd": q_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                }
                st.session_state.consulta = None
            else:
                st.session_state.consulta = t_in
            st.rerun()

    if st.button("🧹 Limpar Lista de Mensagens"):
        st.session_state.radar = {}
        st.session_state.consulta = None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Alta Performance")

# SEÇÃO 1: CONSULTA RÁPIDA (Não polui a lista de monitoramento)
if st.session_state.consulta:
    t_c = st.session_state.consulta
    h_c, info_c, dolar_c, is_c_c = buscar_v190(t_c)
    if h_c is not None and not h_c.empty:
        st.subheader(f"🔍 Consulta Rápida: {t_c}")
        st.metric(f"Preço Agora", f"{h_c['Close'].iloc[-1]:,.2f}")
        fig_c = go.Figure(data=[go.Candlestick(x=h_c.index, open=h_c.Open, high=h_c.High, low=h_c.Low, close=h_c.Close)])
        fig_c.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_c, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO (Lista de Mensagens para Telegram)
if not st.session_state.radar:
    st.info("Nenhuma operação ativa. Preencha os valores para monitorar e enviar alertas.")
else:
    for t_at, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_v190(t_at)
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # CÁLCULO DE LINHAS DE TENDÊNCIA (Pullback e Breakout)
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            
            # Calculadora Blindada (image_356f92.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            lucro_brl = (u_totais * (p_agora * taxa)) - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📈 MONITORANDO PARA MENSAGEM: {t_at}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric("Preço Atual", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with c3:
                    st.subheader("🤖 Mentor Trade Specialist")
                    if cfg['alvo'] > 0:
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 META ATINGIDA!")
                            enviar_telegram(tk, cid, f"💰 VENDA: {t_at} em {p_agora:,.2f}")
                        else:
                            st.info(f"Falta {((cfg['alvo']/p_agora)-1)*100:.2f}% para o alvo.")
                    
                    # SINAIS DE DAY TRADE (Sua sugestão de Pullback/Reteste)
                    if p_agora <= sup * 1.015: st.success("🔥 SINAL: Ponto de Pullback no Suporte (LTA)!")
                    elif p_agora >= res * 0.985: st.error("⚠️ SINAL: Ponto de Breakout na Resistência (LTB)!")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte / LTA")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência / LTB")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")
        st.divider()

time.sleep(30)
st.rerun()
