import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Configuração de Interface High Clarity (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Trade Master", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Inteligência para Day Trade e Dividendos
def analisar_trade(df, info, is_c):
    try:
        p_agora = df['Close'].iloc[-1]
        p_min = df['Low'].rolling(14).min().iloc[-1]
        p_max = df['High'].rolling(14).max().iloc[-1]
        
        # Análise de Dividendos (image_31d3a8.png)
        div_raw = info.get('dividendYield', 0)
        div = (div_raw * 100) if (div_raw and div_raw < 1) else (div_raw if div_raw else 0)
        
        # Mentor Especialista em Day Trade
        msg = f"📍 Suporte em {p_min:,.2f} | 🚩 Resistência em {p_max:,.2f}. "
        if p_agora <= p_min * 1.02:
            msg += "🔥 OPORTUNIDADE: Preço próximo ao suporte (ZONA DE COMPRA)."
        elif p_agora >= p_max * 0.98:
            msg += "⚠️ ALERTA: Preço próximo à resistência (ZONA DE VENDA)."
        else:
            msg += "⚖️ Ativo em zona neutra de negociação."
            
        if not is_c:
            msg += f" | 💰 Dividendos: {div:.2f}%."
            
        return msg, p_min, p_max
    except: return "Aguardando sinal técnico...", 0, 0

@st.cache_data(ttl=30)
def buscar_v120(t):
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

# --- SIDEBAR: CONSULTA E TRADE ---
with st.sidebar:
    st.title("🛡️ Trade Master Pro")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Novo Trade (Day/Swing)")
    
    with st.form("trade_form", clear_on_submit=True):
        t_in = st.text_input("Ticker:").upper().strip()
        p_compra = st.number_input("Preço de Entrada:", min_value=0.0)
        p_venda = st.number_input("Alvo (Gain):", min_value=0.0)
        
        # Ajuste inteligente: Quantidade para Ações, Valor para Cripto
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            valor = st.number_input("Investido (R$):", min_value=0.0)
            qtd = 0
        else:
            qtd = st.number_input("Quantidade:", min_value=0, step=1)
            valor = p_compra * qtd
            
        if st.form_submit_button("✅ Iniciar Monitoramento"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "p_in": p_compra, "alvo": p_venda, "v_brl": valor, "qtd": qtd, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                }
                st.rerun()

    if st.button("🧹 Limpar Lista de Trades"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal de Alta Performance")

if not st.session_state.radar:
    st.info("Terminal pronto para Day Trade. Configure sua entrada na lateral.")
else:
    for t, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_v120(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # Cálculo de Lucro Day Trade (image_25fe79.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            v_inv_brl = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            v_agora_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_agora_brl - v_inv_brl
            
            msg_mentor, sup, res = analisar_trade(h, info, is_c)
            
            with st.expander(f"📉 TRADE ATIVO: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {'US$' if is_c else 'R$'}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t}", key=f"stop_{t}"):
                        del st.session_state.radar[t]
                        st.rerun()
                with c2:
                    st.metric("Resultado (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with c3:
                    st.subheader("🤖 Robo Especialista")
                    st.info(msg_mentor)
                    if cfg['alvo'] > 0:
                        lucro_alvo = (u_totais * (cfg['alvo'] * taxa)) - v_inv_brl
                        st.success(f"🎯 Meta de Lucro: R$ {lucro_alvo:,.2f}")
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 META ATINGIDA! HORA DE REALIZAR O DAY TRADE!")

                # Gráfico com Suporte e Resistência (Kandall)
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dot", line_color="green", annotation_text="Suporte")
                fig.add_hline(y=res, line_dash="dot", line_color="red", annotation_text="Resistência")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t}")
        st.divider()

time.sleep(30)
st.rerun()
