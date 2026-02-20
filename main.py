import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup de Performance (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Trade Specialist", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise Técnica (Day & Swing Trade)
def analisar_sinais(df, info, is_c):
    try:
        p_atual = df['Close'].iloc[-1]
        # Cálculo de Suporte e Resistência (Mínimas e Máximas de 14 dias)
        suporte = df['Low'].rolling(14).min().iloc[-1]
        resistencia = df['High'].rolling(14).max().iloc[-1]
        
        # Correção de Dividendos (image_31d3a8.png)
        div_yield = info.get('dividendYield', 0)
        div = (div_yield * 100) if (div_yield and div_yield < 1) else (div_yield if div_yield else 0)
        
        # Lógica do Mentor Especialista
        status = f"📍 Suporte: {suporte:,.2f} | 🚩 Resistência: {resistencia:,.2f}"
        if p_atual <= suporte * 1.015:
            dica = "🔥 SINAL DE COMPRA: Preço testando o Suporte!"
        elif p_atual >= resistencia * 0.985:
            dica = "⚠️ SINAL DE VENDA: Preço próximo à Resistência!"
        else:
            dica = "⚖️ Zona Neutra: Aguarde melhor ponto de entrada."
            
        return dica, status, div, suporte, resistencia
    except: return "Aguardando sinais...", "", 0, 0, 0

@st.cache_data(ttl=15)
def buscar_dados_v125(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- GESTÃO DE ESTADO (MEMÓRIA BLINDADA) ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: TERMINAL DE OPERAÇÕES ---
with st.sidebar:
    st.title("🛡️ Trade Specialist")
    tk_tg = st.text_input("Token Telegram:", type="password")
    chat_id = st.text_input("Seu ID Telegram:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Abrir Nova Operação")
    
    # Sistema de Inputs independentes para evitar erro de Enter (image_31d45b.png)
    t_input = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
    p_in = st.number_input("Preço de Entrada:", min_value=0.0)
    p_out = st.number_input("Alvo (Take Profit):", min_value=0.0)
    
    if t_input in ["BTC", "XRP", "ETH", "SOL"]:
        investido = st.number_input("Total em Reais (R$):", min_value=0.0)
        quantidade = 0
    else:
        quantidade = st.number_input("Quantidade de Ações:", min_value=0, step=1)
        investido = p_in * quantidade

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Iniciar Trade"):
            if t_input:
                # Chave única por ativo (OHI != MXRF11)
                st.session_state.radar[t_input] = {
                    "p_in": p_in, "alvo": p_out, "v_brl": investido, "qtd": quantidade, "is_c": investido == 0
                }
                st.rerun()
    with c2:
        if st.button("🧹 Limpar Lista"):
            st.session_state.radar = {}
            st.rerun()

# --- PAINEL DE PERFORMANCE ---
st.title("🏛️ InvestSmart Pro | Gestão de Lucro Profissional")

if not st.session_state.radar:
    st.info("Terminal pronto. Configure seu Day Trade ou Swing Trade na lateral.")
else:
    for t, cfg in list(st.session_state.radar.items()):
        df_h, info_at, dolar, is_c = buscar_dados_v125(t)
        
        if df_h is not None and not df_h.empty:
            p_agora = df_h['Close'].iloc[-1]
            cambio = dolar if is_c else 1.0
            
            # Calculadora de Lucro Real (image_25fe79.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * cambio) if is_c else cfg["qtd"]
            v_total_brl = u_totais * (p_agora * cambio)
            lucro_brl = v_total_brl - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
            
            dica, status, div, sup, res = analisar_sinais(df_h, info_at, is_c)
            
            with st.expander(f"📈 OPERAÇÃO ATIVA: {t}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric(f"Preço {'US$' if is_c else 'R$'}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t}", key=f"enc_{t}"):
                        del st.session_state.radar[t]
                        st.rerun()
                with col2:
                    st.metric("Resultado (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with col3:
                    st.subheader("🤖 Mentor Trade Specialist")
                    st.info(f"{status}\n\n{dica}")
                    if not is_c: st.write(f"💰 Dividend Yield: **{div:.2f}%**")
                    if cfg['alvo'] > 0:
                        projecao = (u_totais * (cfg['alvo'] * cambio)) - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
                        st.success(f"🎯 Meta de Ganho: R$ {projecao:,.2f}")

                # Gráfico Kendall com Linhas de Suporte/Resistência (image_242d00.png)
                fig = go.Figure(data=[go.Candlestick(x=df_h.index, open=df_h.Open, high=df_h.High, low=df_h.Low, close=df_h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="Suporte")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="Resistência")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t}")
        st.divider()

time.sleep(30)
st.rerun()
