import os
import ccxt
import time
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Trading Bot Frankfurt ist ONLINE!"

def run_scanner():
    # Wir nutzen beide Namen zur Sicherheit
    api_key = os.environ.get('BYBIT_API_KEY') or os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BYBIT_API_SECRET') or os.environ.get('BYBIT_API_KEY_SECRET')

    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })

    print("--- 🛰️ STARTE APR-SCANNER (FRANKFURT) ---", flush=True)

    while True:
        try:
            balance = exchange.fetch_balance()
            usdc_free = balance.get('USDC', {}).get('free', 0)
            
            ticker = exchange.fetch_ticker('JTO/USDT')
            price = ticker['last']

            print(f"💰 Guthaben: {usdc_free} USDC", flush=True)
            print(f"📊 JTO Preis: {price} USDT", flush=True)
            print("--------------------------------", flush=True)
        except Exception as e:
            print(f"❌ Fehler: {e}", flush=True)
        
        time.sleep(30)

threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
