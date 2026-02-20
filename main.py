import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Layout Profissional (Fundo Claro para Day Trade)
st.set_page_config(page_title="InvestSmart Pro | Expert", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise e Mensageria
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=20)
def buscar_v180(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- INICIALIZAÇÃO DE MEMÓRIA (image_3172e1.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO DE TRADE E CONSULTA ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Consulta ou Monitorar")
    
    # RESOLUÇÃO DO ERRO DE LIMPEZA (image_35735a.png): Chaves controladas
    t_in = st.text_input("Ticker (Ex: VULC3, BTC):", key="f_t").upper().strip()
    p_compra = st.number_input("Preço de Entrada:", key="f_p1", min_value=0.0)
    p_venda = st.number_input("Alvo de Venda:", key="f_p2", min_value=0.0)
    
    if t_in in ["BTC", "XRP", "ETH", "SOL"]:
        v_invest = st.number_input("Valor em Reais (R$):", key="f_v", min_value=0.0)
        q_acoes = 0
    else:
        q_acoes = st.number_input("Qtd Ações:", key="f_q", min_value=0, step=1)
        v_invest = p_compra * q_acoes

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Executar"):
            if t_in:
                # LÓGICA SMART: Se tem valor, monitora. Se não, apenas consulta.
                if p_compra > 0 or p_venda > 0:
                    st.session_state.radar[t_in] = {
                        "p_in": p_compra, "alvo": p_venda, "v_brl": v_invest, "qtd": q_acoes, "is_c": v_invest > 0 and q_acoes == 0
                    }
                    st.session_state.consulta = None
                else:
                    st.session_state.consulta = t_in
                st.rerun()
    with col2:
        if st.button("🧹 Limpar Campos"):
            # RESET SEGURO (image_31d080.png): Limpa chaves sem quebrar a API
            for k in ["f_t", "f_p1", "f_p2", "f_v", "f_q"]:
                st.session_state[k] = "" if k == "f_t" else 0.0
            st.rerun()

    if st.button("🗑️ Parar Todos os Monitoramentos"):
        st.session_state.radar = {}
        st.session_state.consulta = None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Trade Specialist")

# SEÇÃO 1: CONSULTA RÁPIDA (Não entra na lista de mensagens)
if st.session_state.consulta:
    t_c = st.session_state.consulta
    h_c, info_c, dolar_c, is_c_c = buscar_v180(t_c)
    if h_c is not None and not h_c.empty:
        st.subheader(f"🔍 Consulta: {t_c}")
        st.metric(f"Preço Agora ({'US$' if is_c_c else 'R$'})", f"{h_c['Close'].iloc[-1]:,.2f}")
        fig_c = go.Figure(data=[go.Candlestick(x=h_c.index, open=h_c.Open, high=h_c.High, low=h_c.Low, close=h_c.Close)])
        fig_c.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_c, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO (Lista de Mensagens)
if not st.session_state.radar:
    st.info("Nenhuma operação ativa. Preencha os valores para monitorar.")
else:
    for t_at, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_v180(t_at)
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # CÁLCULO DE LINHAS DE TENDÊNCIA (Day Trade)
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            
            # CALCULADORA CORRIGIDA (image_356f92.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            lucro_brl = (u_totais * (p_agora * taxa)) - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📈 TRADE ATIVO: {t_at}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric("Preço Atual", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with c2:
                    st.metric("Resultado (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with c3:
                    st.subheader("🤖 Mentor Trade Specialist")
                    if cfg['alvo'] > 0:
                        # ALERTA DE PRECISÃO (image_356f92.png)
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 META ATINGIDA!")
                            enviar_alerta(tk, cid, f"💰 VENDA: {t_at} em {p_agora:,.2f}")
                        else:
                            st.info(f"Faltam {((cfg['alvo']/p_agora)-1)*100:.2f}% para o alvo de {cfg['alvo']:,.2f}")
                    
                    if p_agora <= sup * 1.015: st.success("🔥 SINAL: Ponto de Pullback no Suporte!")
                    elif p_agora >= res * 0.985: st.error("⚠️ SINAL: Testando Resistência!")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")
        st.divider()

time.sleep(30)
st.rerun()
