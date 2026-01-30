import os
import time
import requests
import threading
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# --- KEYS VON RENDER ---
BYBIT_API_KEY = os.getenv('BYBIT_KEY')
BYBIT_SECRET_KEY = os.getenv('BYBIT_SECRET')
TELEGRAM_TOKEN = "8597158635:AAFL3ah1yxQwXV9ntnChwY9sZRl6mcemt5s"
TELEGRAM_CHAT_ID = 5810124088

# --- SETTINGS ---
MIN_APR_THRESHOLD = 10.0  # Exit unter 10%
SCAN_INTERVAL = 60        # Scan alle 60 Sek.

# Interner Speicher für die Simulation
account = {"active_positions": {}}

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def get_bybit_apr_live():
    """Holt die echten Live-APR von Bybit Flexible Savings"""
    url = "https://api.bybit.com/v5/earn/product-info"
    params = {"category": "FlexibleSaving"}
    try:
        # Öffentliche Abfrage der Earn-Produkte
        response = requests.get(url, params=params, timeout=10).json()
        if response.get("retCode") == 0:
            products = response["result"]["list"]
            # Umrechnung in Prozent: 0.113 -> 11.3%
            return {p["coin"]: float(p["estimateApr"]) * 100 for p in products}
    except Exception as e:
        print(f"Bybit API Error: {e}")
    return {}

@app.route('/')
def home():
    # Diese Seite wird von cron-job.org alle 5 Min aufgerufen
    return f"Bot ist wach. Letzter Check: {datetime.now().strftime('%H:%M:%S')}"

def trading_logic():
    send_telegram("🚀 *Live-Daten-Scanner gestartet!* (Trockenübung)")
    
    while True:
        # 1. Echte Bybit Daten holen
        bybit_live = get_bybit_apr_live()
        
        # 2. Binance Vergleichswerte (Simulation)
        binance_sim = {"AXS": 115.0, "MOVE": 45.0, "SAFE": 8.0} 
        
        # Alle verfügbaren Coins sammeln
        all_coins = set(bybit_live.keys()) | set(binance_sim.keys())
        
        for coin in ["AXS", "MOVE", "SAFE"]: # Fokus auf deine Top-Coins
            apr_bybit = bybit_live.get(coin, 0)
            apr_binance = binance_sim.get(coin, 0)
            
            best_apr = max(apr_bybit, apr_binance)
            source = "Bybit (LIVE)" if apr_bybit > apr_binance else "Binance (SIM)"

            # EXIT LOGIK
            if coin in account['active_positions']:
                if best_apr < MIN_APR_THRESHOLD:
                    del account['active_positions'][coin]
                    send_telegram(f"📉 *ALARM - SELL:* {coin}\nAPR auf {best_apr:.2f}% gefallen ({source}).\nPosition (virtuell) geschlossen.")

            # ENTRY LOGIK
            elif best_apr > 20.0 and len(account['active_positions']) < 3:
                account['active_positions'][coin] = {"apr": best_apr, "source": source}
                send_telegram(f"💎 *CHANCE:* {coin}\n🔥 Echtzeit APR: {best_apr:.2f}%\n🏦 Quelle: {source}\nStatus: Trockenübung läuft.")

        time.sleep(SCAN_INTERVAL)

# Bot-Logik in separatem Thread starten
threading.Thread(target=trading_logic, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
