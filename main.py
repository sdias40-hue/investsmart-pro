import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Setup Visual High Clarity (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Trade Specialist", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Análise para Day Trade e Swing Trade
def analisar_sinais_v130(df, info, is_c):
    try:
        p_atual = df['Close'].iloc[-1]
        # Linhas de Suporte e Resistência (Mínimas/Máximas de 14 dias)
        sup = df['Low'].rolling(14).min().iloc[-1]
        res = df['High'].rolling(14).max().iloc[-1]
        
        # Correção de Dividendos (image_31d3a8.png)
        div_raw = info.get('dividendYield', 0)
        div = (div_raw * 100) if (div_raw and div_raw < 1) else (div_raw if div_raw else 0)
        
        # Mentor de Tendência (Day Trade)
        tendencia = "Alta" if p_atual > df['Close'].mean() else "Baixa"
        dica = f"📈 Tendência: {tendencia} | 📍 Suporte: {sup:,.2f} | 🚩 Resistência: {res:,.2f}"
        
        if p_atual <= sup * 1.015:
            conselho = "🔥 OPORTUNIDADE: Preço em zona de Suporte. Melhor hora para COMPRA!"
        elif p_atual >= res * 0.985:
            conselho = "⚠️ ALERTA: Preço em zona de Resistência. Hora de considerar VENDA!"
        else:
            conselho = "⚖️ Zona Neutra: Aguarde aproximação das linhas para operar."
            
        return dica, conselho, div, sup, res
    except: return "Aguardando sinais...", "Processando...", 0, 0, 0

@st.cache_data(ttl=15)
def buscar_dados_v130(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.60, False

# --- GESTÃO DE MEMÓRIA (Fim da troca OHI por MXRF11) ---
if 'monitor' not in st.session_state: st.session_state.monitor = {}

# --- SIDEBAR: COMANDO DE TRADE ---
with st.sidebar:
    st.title("🛡️ Trade Specialist")
    tk_tg = st.text_input("Token Telegram:", type="password")
    c_id = st.text_input("ID Telegram:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Novo Trade")
    
    # Sistema de Inputs independentes para evitar erro de Enter (image_31d45b.png)
    t_input = st.text_input("Ticker (Ex: VULC3, BTC):", key="t_in").upper().strip()
    p_compra = st.number_input("Preço de Entrada:", key="p_in", min_value=0.0)
    p_alvo = st.number_input("Alvo (Take Profit):", key="p_out", min_value=0.0)
    
    if t_input in ["BTC", "XRP", "ETH", "SOL"]:
        valor_r = st.number_input("Total em Reais (R$):", key="v_r", min_value=0.0)
        qtd_a = 0
    else:
        qtd_a = st.number_input("Quantidade Ações:", key="q_a", min_value=0, step=1)
        valor_r = p_compra * qtd_a

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Iniciar Trade"):
            if t_input:
                st.session_state.monitor[t_input] = {
                    "p_in": p_compra, "alvo": p_alvo, "v_brl": valor_r, "qtd": qtd_a, "is_c": valor_r == 0
                }
                st.rerun()
    with c2:
        if st.button("🧹 Limpar Campos"):
            # RESET SEGURO (image_33b827.png): Limpa apenas a lateral
            for k in ["t_in", "p_in", "p_out", "v_r", "q_a"]:
                st.session_state[k] = "" if k == "t_in" else 0.0
            st.rerun()

    if st.button("🗑️ Parar Monitoramento"):
        st.session_state.monitor = {}
        st.rerun()

# --- PAINEL DE PERFORMANCE ---
st.title("🏛️ InvestSmart Pro | Terminal Trade Master")

if not st.session_state.monitor:
    st.info("Terminal pronto. Configure seu Day Trade ou Swing Trade na lateral.")
else:
    for t, cfg in list(st.session_state.monitor.items()):
        df_h, info_at, dolar, is_c = buscar_dados_v103(t) # Compatibilidade de busca
        
        if df_h is not None and not df_h.empty:
            p_agora = df_h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # Calculadora de Lucro (image_25fe79.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            v_inv_brl = cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"])
            v_atual_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_atual_brl - v_inv_brl
            
            dica_t, conselho_m, div, sup, res = analisar_sinais_v130(df_h, info_at, is_c)
            
            with st.expander(f"📈 OPERAÇÃO: {t}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.metric(f"Preço {'US$' if is_c else 'R$'}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t}", key=f"stop_{t}"):
                        del st.session_state.monitor[t]
                        st.rerun()
                with col2:
                    st.metric("Resultado (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                with col3:
                    st.subheader("🤖 Mentor Trade Specialist")
                    st.write(dica_t)
                    st.info(conselho_m)
                    if not is_c: st.write(f"💰 Dividendos: **{div:.2f}%**")
                    if cfg['alvo'] > 0:
                        proj = (u_totais * (cfg['alvo'] * taxa)) - v_inv_brl
                        st.success(f"🎯 Meta de Lucro: R$ {proj:,.2f}")

                # Gráfico com Linhas Técnicas (image_242d00.png)
                fig = go.Figure(data=[go.Candlestick(x=df_h.index, open=df_h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="SUPORTE")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="RESISTÊNCIA")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t}")
        st.divider()

time.sleep(30)
st.rerun()
