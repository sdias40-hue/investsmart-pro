import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import time

# 1. Configuração de Interface Profissional (image_df2bc5.jpg)
st.set_page_config(page_title="InvestSmart Pro | Elite", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca e Inteligência Blindado
@st.cache_data(ttl=20)
def buscar_dados_v260(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        # Busca direta: USD para Cripto e B3 para Ações (image_4144be.jpg)
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        
        if h.empty: return None
        
        # Filtro de Dados: Só calcula Preço Justo e DPA para Ações
        dados = {"h": h, "info": tk.info, "dolar": usd_brl, "is_c": is_c}
        if not is_c:
            lpa = tk.info.get('forwardEps', 0)
            vpa = tk.info.get('bookValue', 0)
            dados["pj"] = np.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
            dados["dpa"] = tk.info.get('dividendRate', 0)
            div_raw = tk.info.get('dividendYield', 0)
            dados["div"] = (div_raw * 100) if (div_raw and div_raw < 1) else div_raw
        else:
            dados["pj"], dados["dpa"], dados["div"] = 0, 0, 0
            
        return dados
    except: return None

def enviar_msg(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

# --- ESTADOS DE MEMÓRIA (image_3172e1.png) ---
if 'radar' not in st.session_state: st.session_state.radar = {}
if 'consulta' not in st.session_state: st.session_state.consulta = None

# --- SIDEBAR: COMANDO CENTRAL (Resolve image_41ae5a.png) ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    # Chaves fixas evitam o erro de NameError
    tkn = st.text_input("Token Telegram:", type="password", key="tk_bot")
    cid = st.text_input("Seu ID:", value="8392660003", key="id_bot")
    
    st.divider()
    st.subheader("🚀 Análise e Trade")
    
    with st.form("form_v260", clear_on_submit=True):
        t_in = st.text_input("Ticker (VULC3, BTC):").upper().strip()
        p_ent = st.number_input("Preço Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_alv = st.number_input("Alvo Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_inv = st.number_input("Valor Investido (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Qtd Ações:", min_value=0, step=1)
            v_inv = p_ent * q_a
            
        if st.form_submit_button("🚀 Analisar e Iniciar"):
            if t_in:
                if p_ent > 0 or p_alv > 0:
                    st.session_state.radar[t_in] = {
                        "p_in": p_ent, "alvo": p_alv, "v_brl": v_inv, "qtd": q_a, "is_c": q_a == 0
                    }
                    st.session_state.consulta = None
                else:
                    st.session_state.consulta = t_in
                st.rerun()

    if st.button("🧹 Limpar Monitoramento"):
        st.session_state.radar = {}
        st.session_state.consulta = None
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ InvestSmart Pro | Terminal Multi-Ativos")

# SEÇÃO 1: CONSULTA DE DECISÃO (Resolve image_41509d.png)
if st.session_state.consulta:
    d = buscar_dados_v260(st.session_state.consulta)
    if d:
        p_atual = d['h']['Close'].iloc[-1]
        moeda = "US$" if d['is_c'] else "R$"
        st.subheader(f"🔍 Decisão Estratégica: {st.session_state.consulta}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"Preço {moeda}", f"{p_atual:,.2f}")
        
        if not d['is_c']:
            c2.metric("Preço Justo", f"R$ {d['pj']:,.2f}")
            c3.metric("DPA Projetado", f"R$ {d['dpa']:,.2f}/ação")
            c4.metric("Div. Yield", f"{d['div']:.2f}%")
        else:
            c2.metric("Market Cap", f"US$ {d['info'].get('marketCap', 0)/1e9:.1f}B")
            c3.metric("Cotação R$", f"R$ {p_atual * d['dolar']:,.2f}")
            c4.metric("Vol 24h", f"US$ {d['info'].get('volume', 0)/1e6:.1f}M")

        figc = go.Figure(data=[go.Candlestick(x=d['h'].index, open=d['h'].Open, high=d['h'].High, low=d['h'].Low, close=d['h'].Close)])
        figc.update_layout(height=350, template='plotly_white', xaxis_rangeslider_visible=False)
        st.plotly_chart(figc, use_container_width=True)
    st.divider()

# SEÇÃO 2: MONITORAMENTO ATIVO
if st.session_state.radar:
    for t_at, cfg in list(st.session_state.radar.items()):
        d_at = buscar_dados_v260(t_at)
        if d_at:
            p_now = d_at['h']['Close'].iloc[-1]
            tx = d_at['dolar'] if d_at['is_c'] else 1.0
            
            # Lucro Real (image_25fe79.png)
            u_tot = cfg["v_brl"] / (cfg["p_in"] * tx) if d_at['is_c'] else cfg["qtd"]
            lucro = (u_tot * (p_now * tx)) - (cfg["v_brl"] if d_at['is_c'] else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📈 VIGIANDO: {t_at}", expanded=True):
                col1, col2, col3 = st.columns([1, 1, 2])
                col1.metric("Preço", f"{p_now:,.2f}")
                col2.metric("Lucro R$", f"R$ {lucro:,.2f}")
                
                if st.button(f"Encerrar {t_at}", key=f"stop_{t_at}"):
                    del st.session_state.radar[t_at]
                    st.rerun()
                
                with col3:
                    if cfg['alvo'] > 0:
                        if p_now >= cfg['alvo']:
                            st.warning("🚨 META ATINGIDA!")
                            enviar_msg(st.session_state.tk_bot, st.session_state.id_bot, f"💰 ALVO: {t_at} em {p_now:,.2f}")
                        else:
                            st.info(f"Falta {((cfg['alvo']/p_now)-1)*100:.2f}% para o alvo.")

                fig = go.Figure(data=[go.Candlestick(x=d_at['h'].index, open=d_at['h'].Open, high=d_at['h'].High, low=d_at['h'].Low, close=d_at['h'].Close)])
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True, key=f"gr_{t_at}")

time.sleep(30)
st.rerun()
