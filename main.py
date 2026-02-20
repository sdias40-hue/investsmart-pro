import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Interface High Clarity (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Professional", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Funções de Suporte e Mensagem
def enviar_telegram(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v150(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.65, False

# --- INICIALIZAÇÃO DE MEMÓRIA ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: COMANDO DE OPERAÇÕES ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Novo Monitoramento")
    
    # FORMULÁRIO COM LIMPEZA AUTOMÁTICA (Sua Sugestão)
    with st.form("trade_form", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
        p_compra = st.number_input("Preço de Compra (R$ ou US$):", min_value=0.0, format="%.2f")
        p_alvo = st.number_input("Alvo de Venda (R$ ou US$):", min_value=0.0, format="%.2f")
        
        # Lógica Adaptada: Quantidade para Ações, Valor para Cripto (image_2615ba.png, image_259617.png)
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Total Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Quantidade de Ações:", min_value=0, step=1)
            v_brl = p_compra * q_a
            
        if st.form_submit_button("🚀 Monitorar e Limpar"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "p_in": p_compra, "alvo": p_alv, "v_brl": v_brl, "qtd": q_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                }
                st.rerun()

    if st.button("🗑️ Parar Todos os Monitoramentos"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Performance")

if not st.session_state.radar:
    st.info("Terminal pronto. Configure seu trade na lateral.")
else:
    for t, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_v150(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # CÁLCULO DE LINHAS TÉCNICAS (Sua sugestão de Pullback/Rompimento)
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            media_curta = h['Close'].rolling(7).mean().iloc[-1]
            
            # Calculadora de Lucro (Ação vs Cripto - image_25fe79.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            v_inv_total = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            lucro_brl = (u_totais * (p_agora * taxa)) - v_inv_total
            
            with st.expander(f"📊 MONITORANDO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {'US$' if is_c else 'R$'}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t}", key=f"stop_{t}"):
                        del st.session_state.radar[t]
                        st.rerun()
                with c2:
                    st.metric("Resultado (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                
                with c3:
                    st.subheader("🤖 Mentor Estratégico Specialist")
                    # Lógica de Alvo Corrigida (Cripto US$ vs R$ - image_349ddd.png)
                    if cfg['alvo'] > 0:
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO! HORA DE REALIZAR LUCRO!")
                            enviar_telegram(tk, cid, f"💰 VENDA: {t} atingiu o alvo de {p_agora:,.2f}!")
                        else:
                            st.info(f"💡 Falta {((cfg['alvo']/p_agora)-1)*100:.2f}% para o seu alvo.")
                    
                    # ANÁLISE DE KENDALL (Pullback, Rompimento e Canais)
                    if p_agora <= sup * 1.01:
                        st.success("🔥 TRADE DE CONTINUIDADE: Preço no Suporte. Ótimo ponto para COMPRA (Pullback)!")
                    elif p_agora >= res * 0.99:
                        st.error("⚠️ RESISTÊNCIA DO CANAL: Hora de vender ou aguardar rompimento!")
                    elif p_agora > media_curta:
                        st.write("📈 TENDÊNCIA DE ALTA: Preço trabalhando acima da média curta.")
                    else:
                        st.write("📉 TENDÊNCIA DE BAIXA: Força vendedora predominante.")

                # Gráfico Kendall com Suporte e Resistência (image_242d00.png)
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte (Ponto de Pullback)")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência (Ponto de Breakout)")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{t}")
        st.divider()

time.sleep(30)
st.rerun()
