import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Suporte Blindadas
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_dados(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        ticker = yf.Ticker(search)
        h = ticker.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, usd_brl, is_c
    except: return None, 5.65, False

# --- INICIALIZAÇÃO DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: CONTROLE DE ENTRADA ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🔍 Configurar Novo Monitor")
    
    # FORMULÁRIO: A solução definitiva para o "Enter" não apagar tudo
    with st.form("config_ativo", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3 ou BTC):").upper().strip()
        
        st.write("---")
        # Campos que só são processados ao clicar no botão de confirmação
        p_ent = st.number_input("Preço de Compra (R$ ou US$):", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo para Alerta (R$ ou US$):", min_value=0.0, format="%.2f")
        
        # Lógica de entrada dinâmica
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_inv = st.number_input("Valor Total Investido (R$):", min_value=0.0, step=100.0)
            qtd_a = 0
        else:
            qtd_a = st.number_input("Quantidade de Ações:", min_value=0, step=1)
            v_inv = p_ent * qtd_a

        submitted = st.form_submit_button("🚀 Confirmar para Monitoramento")
        
        if submitted and t_in:
            st.session_state.radar[t_in] = {
                "p_in": p_ent, "alvo": p_alv, "v_brl": v_inv, "qtd": qtd_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
            }
            st.success(f"Monitorando {t_in}!")

    st.divider()
    if st.button("🧹 Limpar Lateral"):
        st.rerun()
    
    if st.button("🗑️ Parar Todas as Mensagens"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Multi-Ativos")

if not st.session_state.radar:
    st.info("Aguardando ativos. Preencha o formulário ao lado.")
else:
    for t_mon in list(st.session_state.radar.keys()):
        cfg = st.session_state.radar[t_mon]
        h, dolar, is_c = buscar_dados(t_mon)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            moeda = "US$" if is_c else "R$"
            
            # Cálculo de Unidades e Valor Atual
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c and cfg["p_in"] > 0 else cfg["qtd"]
            v_atual_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_atual_brl - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📊 MONITORANDO: {t_mon}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {moeda}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_mon}", key=f"del_{t_mon}"):
                        del st.session_state.radar[t_mon]
                        st.rerun()
                with c2:
                    st.metric("Resultado (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                
                with c3:
                    st.subheader("🤖 Mentor Estratégico")
                    if cfg['alvo'] > 0:
                        distancia = ((cfg['alvo'] / p_agora) - 1) * 100
                        st.write(f"🎯 **Alvo Definido:** {moeda} {cfg['alvo']:,.2f}")
                        st.write(f"📈 **Faltam:** {distancia:.2f}% para atingir o objetivo.")
                        
                        # Correção da Lógica de Alerta (Só dispara se o preço superar o alvo)
                        if p_agora >= cfg['alvo']:
                            st.error("🚨 ALVO ATINGIDO! HORA DE VENDER?")
                            enviar_alerta(tk, cid, f"💰 ALVO ATINGIDO: {t_mon} está em {moeda} {p_agora:,.2f}!")
                        else:
                            st.info("💡 Mentor: Mantenha a posição. O ativo ainda está abaixo da sua meta.")

                # Gráfico
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.update_layout(height=350, margin=dict(l=0,r=0,t=0,b=0), template="plotly_white", xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_mon}")

time.sleep(30)
st.rerun()
