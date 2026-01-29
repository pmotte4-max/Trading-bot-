import os
import ccxt
import time
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Trading Bot Frankfurt: Bybit (Scanner) & Binance (Trader) sind BEREIT!"

def run_scanner():
    # 1. Verbindung zu Bybit (Frühwarnsystem / Preis-Sensor)
    bybit = ccxt.bybit({
        'apiKey': os.environ.get('BYBIT_API_KEY'),
        'secret': os.environ.get('BYBIT_API_SECRET'),
        'enableRateLimit': True,
    })

    # 2. Verbindung zu Binance (Dein Handelsplatz)
    binance = ccxt.binance({
        'apiKey': os.environ.get('BINANCE_API_KEY'),
        'secret': os.environ.get('BINANCE_API_SECRET'),
        'enableRateLimit': True,
    })

    print("--- 🛰️ BOT STARTET: MULTI-EXCHANGE MODE (FRANKFURT) ---", flush=True)

    while True:
        try:
            # Daten von Bybit abrufen (Unser Sensor für JTO)
            ticker_bybit = bybit.fetch_ticker('JTO/USDT')
            price_bybit = ticker_bybit['last']
            
            # Guthaben von Binance abrufen (Alle relevanten Währungen)
            bal_binance = binance.fetch_balance()
            
            usdc_binance = bal_binance.get('USDC', {}).get('free', 0)
            usdt_binance = bal_binance.get('USDT', {}).get('free', 0)
            bnb_binance = bal_binance.get('BNB', {}).get('free', 0)

            # Saubere Anzeige in den Render-Logs
            print(f"📡 SENSOR (Bybit) - JTO: {price_bybit} USDT", flush=True)
            print(f"🏦 KAPITAL (Binance): {usdc_binance} USDC | {usdt_binance} USDT", flush=True)
            print(f"⛽ GEBÜHREN (Binance): {bnb_binance} BNB", flush=True)
            print("--------------------------------------------------", flush=True)

        except Exception as e:
            print(f"❌ Fehler bei Abfrage: {e}", flush=True)
        
        # Alle 30 Sekunden scannen
        time.sleep(30)

# Startet den Bot-Prozess im Hintergrund
threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    # Port für Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
