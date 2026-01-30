import os
import time
import requests
import threading
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# --- DEINE DATEN ---
TELEGRAM_TOKEN = "8597158635:AAFL3ah1yxQwXV9ntnChwY9sZRl6mcemt5s"
TELEGRAM_CHAT_ID = 5810124088

# --- SETTINGS ---
MIN_APR_THRESHOLD = 10.0  # Exit, wenn unter 10%
SCAN_INTERVAL = 60        # Alle 60 Sekunden (reicht für Zinsen völlig aus)

# Speicher für aktive Trades
account = {"active_positions": {}}

def get_binance_apr():
    """Holt Daten von Binance Simple Earn (Beispiel-Endpunkt)"""
    try:
        # Hinweis: Binance API erfordert oft für Earn-Daten einen Key. 
        # Wir nutzen hier den öffentlichen Markt-Ticker als Preis-Basis 
        # und simulieren die Earn-Zins-Logik für den ersten Live-Abgleich.
        url = "https://api.binance.com/api/v3/ticker/24hr"
        # Hier filtern wir normalerweise die Earn-Liste
        return {"AXS": 42.5, "MOVE": 35.0, "SAFE": 12.0} 
    except:
        return {}

def get_bybit_apr():
    """Holt Daten von Bybit Flexible Staking"""
    try:
        # Bybit öffentlicher Markt-Check
        url = "https://api.bybit.com/v5/market/tickers?category=spot"
        # Beispiel-Rückgabe für den Vergleich
        return {"AXS": 48.2, "MOVE": 31.5, "SAFE": 9.5}
    except:
        return {}

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except: pass

@app.route('/')
def home():
    return f"Duo-Scanner Online. Letzter Check: {datetime.now().strftime('%H:%M:%S')}"

def trading_logic():
    send_telegram("🛰️ *Dual-Börsen-Scanner aktiv!*\nVergleiche jetzt Binance & Bybit...")
    
    while True:
        binance_data = get_binance_apr()
        bybit_data = get_bybit_apr()
        
        # Alle Coins aus beiden Quellen sammeln
        all_coins = set(binance_data.keys()) | set(bybit_data.keys())
        
        for coin in all_coins:
            apr_binance = binance_data.get(coin, 0)
            apr_bybit = bybit_data.get(coin, 0)
            
            # Wo ist es besser?
            best_apr = max(apr_binance, apr_bybit)
            source = "Binance" if apr_binance > apr_bybit else "Bybit"

            # 1. VERKAUFS-LOGIK (Wenn in Portfolio und APR crashed)
            if coin in account['active_positions']:
                if best_apr < MIN_APR_THRESHOLD:
                    del account['active_positions'][coin]
                    send_telegram(f"🔻 *ALARM - SELL:* {coin}\nAPR auf {best_apr}% gefallen ({source}).\nKapital abgezogen!")

            # 2. KAUF-LOGIK (Wenn Chance > 25% und Platz im Depot)
            elif best_apr > 25.0 and len(account['active_positions']) < 3:
                account['active_positions'][coin] = {"apr": best_apr, "source": source}
                send_telegram(f"💎 *TOP CHANCE:* {coin}\n🔥 APR: {best_apr}%\n🏦 Börse: {source}\nStatus: Position eröffnet.")

        time.sleep(SCAN_INTERVAL)

threading.Thread(target=trading_logic, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
