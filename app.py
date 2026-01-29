import os
import ccxt
import time
from flask import Flask
import threading
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return "Trading Bot Frankfurt ist ONLINE und aktiv!"

def run_scanner():
    # Verbindung zu Bybit
    exchange = ccxt.bybit({
        'apiKey': os.environ.get('BINANCE_API_KEY'),
        'secret': os.environ.get('BYBIT_API_KEY'),
        'enableRateLimit': True,
    })

    print("--- 🛰️ STARTE APR-SCANNER (FRANKFURT) ---", flush=True)

    while True:
        try:
            # Kontostand abrufen
            balance = exchange.fetch_balance()
            # Wir suchen gezielt nach USDC im Unified Account
            usdc_free = balance.get('USDC', {}).get('free', 0)
            
            # JTO Preis abrufen
            ticker = exchange.fetch_ticker('JTO/USDT')
            price = ticker['last']

            print(f"💰 Guthaben: {usdc_free} USDC", flush=True)
            print(f"📊 JTO Preis: {price} USDT", flush=True)
            print("--------------------------------", flush=True)

        except Exception as e:
            print(f"❌ Fehler: {e}", flush=True)

        time.sleep(30)

# Bot in eigenem Thread starten
threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
