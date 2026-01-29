import os
import ccxt
import time
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Trading Bot Frankfurt ist ONLINE"

def run_scanner():
    print("--- 🛰️ STARTE APR-SCANNER (FRANKFURT) ---")
    
    # Verbindung zu Bybit mit deinen Keys aus Render
    exchange = ccxt.bybit({
        'apiKey': os.environ.get('BINANCE_API_KEY'), 
        'secret': os.environ.get('BYBIT_API_KEY'),  
        'enableRateLimit': True,
    })

    while True:
        try:
            # Kontostand im Unified Trading Account prüfen
            balance = exchange.fetch_balance()
            usdc_free = balance.get('USDC', {}).get('free', 0)
            
            # Beispiel: JTO Preis abfragen
            ticker = exchange.fetch_ticker('JTO/USDT')
            
            print(f"💰 Guthaben: {usdc_free} USDC")
            print(f"📊 JTO Preis: {ticker['last']} USDT")
            print("---------------------------------------")
            
        except Exception as e:
            print(f"❌ Fehler: {e}")
        
        time.sleep(30) # Alle 30 Sekunden scannen

if __name__ == "__main__":
    threading.Thread(target=run_scanner).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
