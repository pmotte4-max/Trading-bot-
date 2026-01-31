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
MIN_APR_THRESHOLD = 10.0  
SCAN_INTERVAL = 60        

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
        response = requests.get(url, params=params, timeout=10).json()
        if response.get("retCode") == 0:
            products = response["result"]["list"]
            # Erstellt Liste mit {Coin: APR in %}
            return {p["coin"]: float(p["estimateApr"]) * 100 for p in products}
    except Exception as e:
        print(f"Bybit API Error: {e}")
    return {}

@app.route('/')
def home():
    return f"<h1>Trading Bot Status</h1><p>Scanner aktiv. Letzter Check: {datetime.now().strftime('%H:%M:%S')}</p>"

def trading_logic():
    send_telegram("📡 *Echtzeit-Scanner aktiviert!* Ich ziehe jetzt Live-Daten von Bybit.")
    
    while True:
        bybit_live = get_bybit_apr_live()
        focus_coins = ["AXS", "MOVE", "SAFE"]
        
        for coin in focus_coins:
            best_apr = bybit_live.get(coin, 0.0)
            
            if coin in account['active_positions']:
                if best_apr < MIN_APR_THRESHOLD:
                    del account['active_positions'][coin]
                    send_telegram(f"📉 *ALARM - SELL:* {coin}\nAPR auf {best_apr:.2f}% gefallen.\n(Simulation: Position geschlossen)")
            elif best_apr > 20.0 and len(account['active_positions']) < 3:
                account['active_positions'][coin] = {"apr": best_apr}
                send_telegram(f"💎 *LIVE-CHANCE:* {coin}\n🔥 Echtzeit APR: {best_apr:.2f}%\n🏦 Börse: Bybit\nStatus: Trockenübung läuft.")
        
        time.sleep(SCAN_INTERVAL)

threading.Thread(target=trading_logic, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
