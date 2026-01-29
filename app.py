import os
import ccxt
import time
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Trading Bot Frankfurt: Diagnose-Modus AKTIV!"

def run_scanner():
    bybit = ccxt.bybit({'apiKey': os.environ.get('BYBIT_API_KEY'), 'secret': os.environ.get('BYBIT_API_SECRET'), 'enableRateLimit': True})
    binance = ccxt.binance({'apiKey': os.environ.get('BINANCE_API_KEY'), 'secret': os.environ.get('BINANCE_API_SECRET'), 'enableRateLimit': True})

    print("--- 🛰️ BOT STARTET: DIAGNOSE-MODUS ---", flush=True)

    while True:
        # TEIL 1: BYBIT SCAN (Sollte immer gehen)
        try:
            ticker = bybit.fetch_ticker('JTO/USDT')
            print(f"✅ Bybit Sensor OK - JTO: {ticker['last']} USDT", flush=True)
        except Exception as e:
            print(f"❌ Bybit Fehler: {e}", flush=True)

        # TEIL 2: BINANCE CHECK (Hier suchen wir den Fehler)
        try:
            bal = binance.fetch_balance()
            usdc = bal.get('USDC', {}).get('free', 0)
            print(f"✅ Binance Verbindung OK - Guthaben: {usdc} USDC", flush=True)
        except Exception as e:
            print(f"⚠️ Binance API zickt noch: {e}", flush=True)
            print("Tipp: Prüfe die Keys in Render auf Leerzeichen!", flush=True)

        print("--------------------------------------------------", flush=True)
        time.sleep(30)

threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
