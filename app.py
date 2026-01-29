import os
import ccxt
import time
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Trading Bot Frankfurt: Bybit-Scanner & Binance-Trader sind AKTIV!"

def run_scanner():
    # 1. Verbindung zu Bybit (Unser Frühwarnsystem/Sensor)
    bybit = ccxt.bybit({
        'apiKey': os.environ.get('BYBIT_API_KEY'),
        'secret': os.environ.get('BYBIT_API_SECRET'),
        'enableRateLimit': True,
    })

    # 2. Verbindung zu Binance (Dein eigentlicher Handelsplatz)
    binance = ccxt.binance({
        'apiKey': os.environ.get('BINANCE_API_KEY'),
        'secret': os.environ.get('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })

    print("--- 🛰️ BOT STARTET: ZWEI-BÖRSEN-MODUS ---", flush=True)

    while True:
        try:
            # Daten von Bybit abrufen (Preis-Sensor)
            ticker_bybit = bybit.fetch_ticker('JTO/USDT')
            price_bybit = ticker_bybit['last']
            
            # Guthaben von Binance abrufen (Handels-Kapital)
            bal_binance = binance.fetch_balance()
            # Wir schauen nach USDT auf Binance
            usdt_binance = bal_binance.get('USDT', {}).get('free', 0)

            print(f"📡 Bybit Sensor (JTO): {price_bybit} USDT", flush=True)
            print(f"🏦 Binance Kapital: {usdt_binance} USDT", flush=True)
            print("-----------------------------------------", flush=True)

        except Exception as e:
            # Falls ein Key nicht stimmt, sehen wir es hier sofort
            print(f"❌ Fehler bei Abfrage: {e}", flush=True)
        
        # Alle 30 Sekunden aktualisieren
        time.sleep(30)

# Startet den Bot-Prozess im Hintergrund
threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    # Port-Einstellung für Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
