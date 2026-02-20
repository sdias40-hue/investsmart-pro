import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Inteligência Corrigidas
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=60)
def buscar_analise_v111(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        info = tk.info
        hist = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        # CORREÇÃO DIVIDENDOS (image_31d3a8.png): Escala de % corrigida
        div_raw = info.get('dividendYield', 0)
        # Se o valor vier como decimal (0.05) vira 5%, se vier como 5 vira 5%
        div = (div_raw * 100) if (div_raw and div_raw < 1) else (div_raw if div_raw else 0)
        
        mentor_msg = f"📊 Analisando {t_up}: "
        if is_c:
            mentor_msg += "Forte volatilidade. O Mentor recomenda cautela no gerenciamento de risco."
        else:
            mentor_msg += f"Dividendos estimados em {div:.2f}%. "
            mentor_msg += "Ação com ótimo perfil de renda passiva." if div > 5 else "Foco em valorização de capital."
            
        return hist, mentor_msg, usd_brl, is_c
    except: return None, "Buscando dados...", 5.65, False

# --- INICIALIZAÇÃO DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: CONTROLE TOTAL (image_31d45b.png) ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Monitorar Novo Ativo")
    
    # RESOLUÇÃO DO ENTER (image_31d45b.png): Chaves dinâmicas com verificação de estado
    t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):", key="f_t").upper().strip()
    is_c = t_in in ["BTC", "XRP", "ETH", "SOL"]
    
    if is_c:
        v_inv = st.number_input("Valor Investido (R$):", key="f_v", min_value=0.0)
        p_ent = st.number_input("Preço Compra (US$):", key="f_pc", min_value=0.0)
        p_alv = st.number_input("Alvo Venda (US$):", key="f_pa", min_value=0.0)
        qtd_a = 0
    else:
        p_ent = st.number_input("Preço Compra (R$):", key="f_pca", min_value=0.0)
        qtd_a = st.number_input("Quantidade de Ações:", key="f_q", min_value=0, step=1)
        p_alv = st.number_input("Alvo Venda (R$):", key="f_paa", min_value=0.0)
        v_inv = p_ent * qtd_a

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Monitorar"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "is_c": is_c, "v_brl": v_inv, "p_in": p_ent, "alvo": p_alv, "qtd": qtd_a
                }
                st.rerun()
    with c2:
        if st.button("🧹 Limpar Campos"):
            # RESOLUÇÃO DO ERRO API (image_31d080.png): Reset de campos seguro
            for k in ["f_t", "f_v", "f_pc", "f_pa", "f_pca", "f_q", "f_paa"]:
                if k in st.session_state:
                    st.session_state[k] = "" if k == "f_t" else 0.0
            st.rerun()

    st.divider()
    st.subheader("📋 Mensagens Ativas")
    for t_list in list(st.session_state.radar.keys()):
        st.write(f"🟢 {t_list}")
    
    if st.button("🗑️ Limpar Monitoramento"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Gestão de Lucro Real")

if not st.session_state.radar:
    st.info("Aguardando ativos. Configure na lateral para iniciar o vigia.")
else:
    for t_at in list(st.session_state.radar.keys()):
        cfg = st.session_state.radar[t_at]
        h, mentor_txt, dolar, is_c = buscar_analise_v111(t_at)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            moeda = "US$" if is_c else "R$"
            
            # Calculadora de Lucro (image_315fe4.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c and cfg["p_in"] > 0 else cfg["qtd"]
            v_inv_brl = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            v_atual_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_atual_brl - v_inv_brl
            
            with st.expander(f"📊 MONITORANDO: {t_at}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with col2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with col3:
                    st.subheader("🤖 Mentor Analista")
                    st.info(mentor_txt)
                    if cfg['alvo'] > 0:
                        v_no_alvo = u_totais * (cfg['alvo'] * taxa)
                        st.success(f"🎯 Alvo {moeda} {cfg['alvo']:,.2f} = Lucro R$ {v_no_alvo - v_inv_brl:,.2f}")
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO!")
                            enviar_alerta(tk, cid, f"💰 VENDA: {t_at} atingiu o alvo! Lucro: R$ {lucro_brl:,.2f}")

                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=300, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"v111_{t_at}")
        st.divider()

time.sleep(30)
st.rerun()
