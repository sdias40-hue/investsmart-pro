import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# 1. Layout High Clarity (Fundo Branco para Day Trade)
st.set_page_config(page_title="InvestSmart Pro | Trader", layout="wide")
st.markdown("<style>.main { background-color: #f8f9fa; }</style>", unsafe_allow_html=True)

# 2. Motor de Busca e Mensageria
def enviar_alerta(token, chat_id, msg):
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=5)
        except: pass

@st.cache_data(ttl=30)
def buscar_v140(t):
    try:
        t_up = t.upper().strip()
        is_c = t_up in ["BTC", "XRP", "ETH", "SOL"]
        search = f"{t_up}-USD" if is_c else (f"{t_up}.SA" if "." not in t_up else t_up)
        tk = yf.Ticker(search)
        h = tk.history(period="60d", interval="1d")
        usd_brl = yf.Ticker("BRL=X").history(period="1d")['Close'].iloc[-1]
        return h, tk.info, usd_brl, is_c
    except: return None, None, 5.65, False

# --- MEMÓRIA DO TERMINAL ---
if 'radar' not in st.session_state: st.session_state.radar = {}

# --- SIDEBAR: CENTRO DE COMANDO ---
with st.sidebar:
    st.title("🛡️ Central de Comando")
    tk = st.text_input("Token Telegram:", type="password")
    cid = st.text_input("Seu ID:", value="8392660003")
    
    st.divider()
    st.subheader("🚀 Novo Trade")
    
    # FORMULÁRIO COM LIMPEZA AUTOMÁTICA (Sua sugestão de zerar após monitorar)
    with st.form("trade_form", clear_on_submit=True):
        t_in = st.text_input("Ticker (Ex: VULC3, BTC):").upper().strip()
        p_compra = st.number_input("Preço de Entrada (US$ ou R$):", min_value=0.0, format="%.2f")
        p_alvo = st.number_input("Alvo de Venda (US$ ou R$):", min_value=0.0, format="%.2f")
        
        # Lógica Adaptativa: Quantidade para Ações, Valor para Cripto
        if t_in in ["BTC", "XRP", "ETH", "SOL"]:
            v_brl = st.number_input("Valor Investido Total (R$):", min_value=0.0)
            q_a = 0
        else:
            q_a = st.number_input("Quantidade de Ações:", min_value=0, step=1)
            v_brl = p_compra * q_a
            
        if st.form_submit_button("🚀 Monitorar Ativo"):
            if t_in:
                st.session_state.radar[t_in] = {
                    "p_in": p_compra, "alvo": p_alvo, "v_brl": v_brl, "qtd": q_a, "is_c": t_in in ["BTC", "XRP", "ETH", "SOL"]
                }
                st.rerun()

    if st.button("🧹 Limpar Lista de Trades"):
        st.session_state.radar = {}
        st.rerun()

# --- PAINEL PRINCIPAL ---
st.title("🏛️ Terminal de Alta Performance | Day & Swing Trade")

if not st.session_state.radar:
    st.info("Terminal Pronto. Configure sua entrada na lateral para iniciar o monitoramento.")
else:
    for t, cfg in list(st.session_state.radar.items()):
        h, info, dolar, is_c = buscar_v140(t)
        
        if h is not None and not h.empty:
            p_agora = h['Close'].iloc[-1]
            taxa = dolar if is_c else 1.0
            
            # CÁLCULO DE LINHAS TÉCNICAS (Kendall)
            sup = h['Low'].rolling(14).min().iloc[-1]
            res = h['High'].rolling(14).max().iloc[-1]
            
            # CALCULADORA DE LUCRO (Ação vs Cripto - image_25fe79.png)
            u_totais = cfg["v_brl"] / (cfg["p_in"] * taxa) if is_c else cfg["qtd"]
            v_atual_brl = u_totais * (p_agora * taxa)
            lucro_brl = v_atual_brl - (cfg["v_brl"] if is_c else (cfg["p_in"] * cfg["qtd"]))
            
            with st.expander(f"📊 OPERAÇÃO ATIVA: {t}", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.metric(f"Preço {'US$' if is_c else 'R$'}", f"{p_agora:,.2f}")
                    if st.button(f"Encerrar {t}", key=f"stop_{t}"):
                        del st.session_state.radar[t]
                        st.rerun()
                with c2:
                    st.metric("Resultado (R$)", f"R$ {lucro_brl:,.2f}", f"{((p_agora/cfg['p_in'])-1)*100:.2f}%" if cfg['p_in'] > 0 else "0%")
                
                with c3:
                    st.subheader("🤖 Mentor Analista Specialist")
                    if cfg['alvo'] > 0:
                        # Lógica de Alvo Corrigida (Cripto US$ vs R$ - image_349ddd.png)
                        if p_agora >= cfg['alvo']:
                            st.warning("🚨 ALVO ATINGIDO! HORA DE REALIZAR O LUCRO!")
                            enviar_alerta(tk, cid, f"💰 VENDA: {t} atingiu o alvo de {p_agora:,.2f}!")
                        else:
                            st.info(f"💡 Faltam {((cfg['alvo']/p_agora)-1)*100:.2f}% para o alvo de {cfg['alvo']:,.2f}.")
                    
                    # Explicação da Melhor Hora de Comprar
                    if p_agora <= sup * 1.02:
                        st.success(f"🔥 MELHOR HORA DE COMPRAR: Preço testando o SUPORTE em {sup:,.2f}!")
                    elif p_agora >= res * 0.98:
                        st.error(f"⚠️ HORA DE VENDER: Preço encostando na RESISTÊNCIA em {res:,.2f}!")
                    else:
                        st.write(f"⚖️ Ativo em zona neutra. Suporte: {sup:,.2f} | Resistência: {res:,.2f}")

                # Gráfico com Linhas Técnicas (Kendall)
                fig = go.Figure(data=[go.Candlestick(x=h.index, open=h.Open, high=h.High, low=h.Low, close=h.Close)])
                fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text="SUPORTE (COMPRA)")
                fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text="RESISTÊNCIA (VENDA)")
                fig.update_layout(height=400, template='plotly_white', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{t}")
        st.divider()

time.sleep(30)
st.rerun()
