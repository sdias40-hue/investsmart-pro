import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup de Interface (Foco em Clareza)
st.set_page_config(page_title="InvestSmart Pro | Precision", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Suporte e Análise Técnica
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_dados_v135(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- MEMÓRIA DO TERMINAL ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: CONFIGURAÇÃO DE PRECISÃO ---
with st.sidebar:
    st.title("🛡️ Precision Trade")
    tk_tg = st.text_input("Token Telegram:", type="password")
    c_id = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Configurar Operação")
    
    with st.form("form_trade", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC...):").upper().strip()
        p_entrada = st.number_input("Preço de Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_saida = st.number_input("Alvo de Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Valor Investido (R$):", min_value=0.0)
            qtd_a = 0
        else:
            qtd_a = st.number_input("Quantidade Ações:", min_value=0, step=1)
            v_brl = p_entrada * qtd_a
            
        if st.form_submit_button("🚀 Iniciar Monitoramento"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "p_in": p_entrada, "alvo": p_saida, "v_brl": v_brl, "qtd": qtd_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                }
                st.rerun()

    if st.button("🗑️ Limpar Todos os Trades"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal de Alta Performance")

if not st.session_state.radar:
    st.info("Aguardando novas ordens. Use a lateral para configurar seu trade.")
else:
    for t_at, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_dados_v135(t_at)
        
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
                    st.metric(f"Preço {'US$' if is_c else 'R$'}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                        del st.session_state.radar[t_at]
                        st.rerun()
                with c2:
                    st.metric("Lucro (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                
                with c3:
                    st.subheader("🤖 Mentor Trade Specialist")
                    # Lógica de Alvo Corrigida (Ex: 67k vs 90k)
                    if cfg['alvo'] > 0:
                        falta_p = ((cfg['alvo'] / p_agora) - 1) * 100
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 META ATINGIDA! HORA DE REALIZAR LUCRO!")
                            enviar_alerta(tk_tg, c_id, f"💰 ALVO ATINGIDO: {t_at} chegou em {p_agora:,.2f}!")
                        else:
                            st.info(f"💡 Falta {falta_p:.2f}% para atingir o seu alvo de {cfg['alvo']:,.2f}.")
                    
                    st.write(f"🟢 **Suporte:** {sup:,.2f} | 🔴 **Resistência:** {res:,.2f}")

                # Gráfico com Linhas Técnicas
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="SUPORTE")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="RESISTÊNCIA")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")
        st.divider()

time.sleep(30)
st.rerun()
