import time
import yfinance as yf
import json
import os
import requests

# ==============================================================================
# CONFIGURAÇÕES DO ROBÔ (SunaKortix Monitor)
# ==============================================================================
TELEGRAM_TOKEN = "8677195763:AAEQYz5V6Q-fEcAKhMjq77DH28oWBEnhA6Q"
TELEGRAM_CHAT_ID = "8392660003"

COIN = "BTC-USD" 
STOP_PERCENT = 5.0 
MAX_PRICE_FILE = "highest_price_crypto.json"
DOLAR = 5.50 

def enviar_alerta(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[ERRO] Falha ao enviar Telegram: {e}")

def carregar_maxima():
    if os.path.exists(MAX_PRICE_FILE):
        try:
            with open(MAX_PRICE_FILE, "r") as f:
                dados = json.load(f)
                return dados.get(COIN, 0)
        except:
            return 0
    return 0

def salvar_maxima(preco):
    dados = {COIN: preco}
    with open(MAX_PRICE_FILE, "w") as f:
        json.dump(dados, f)

def monitorar_cripto():
    print(f"🚀 Iniciando SunaKortix Monitor para {COIN}...")
    enviar_alerta(f"🤖 SunaKortix Monitor Ativado!\nVigiando {COIN} com Trailing Stop de {STOP_PERCENT}%.")
    
    highest_price = carregar_maxima()
    
    while True:
        try:
            ticker = yf.Ticker(COIN)
            data = ticker.history(period="1d")
            
            if not data.empty:
                current_price = float(data['Close'].iloc[-1])
            else:
                print("[AVISO] Sem dados recentes do mercado. Tentando novamente...")
                time.sleep(10)
                continue
            
            if highest_price == 0 or current_price > highest_price:
                highest_price = current_price
                salvar_maxima(highest_price)
                print(f"🔥 Nova máxima registrada: US$ {highest_price:,.2f}")
            
            stop_price = highest_price * (1 - (STOP_PERCENT / 100))
            
            print(f"Preço: US$ {current_price:,.2f} (~R$ {current_price*DOLAR:,.2f}) | Stop em: US$ {stop_price:,.2f} | Máxima: US$ {highest_price:,.2f}")
            
            if current_price <= stop_price:
                mensagem_alerta = (
                    f"⚠️ 🚨 **ALERTA DE TRAILING STOP** 🚨 ⚠️\n\n"
                    f"O ativo **{COIN}** caiu abaixo do limite de proteção!\n"
                    f"📈 Maior topo alcançado: US$ {highest_price:,.2f} (~R$ {highest_price*DOLAR:,.2f})\n"
                    f"📉 Preço de disparo do Stop: US$ {stop_price:,.2f} (~R$ {stop_price*DOLAR:,.2f})\n"
                    f"💰 Preço Atual: US$ {current_price:,.2f} (~R$ {current_price*DOLAR:,.2f})"
                )
                enviar_alerta(mensagem_alerta)
                highest_price = current_price
                salvar_maxima(highest_price)
                
        except Exception as e:
            print(f"[ERRO] Falha na leitura do mercado: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    monitorar_cripto()
