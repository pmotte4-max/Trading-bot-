import os
import ccxt
import time
from flask import Flask
import threading
from datetime import datetime

app = Flask(__name__)

# --- VIRTUELLES TEST-KONTO (3 Coins gleichzeitig möglich) ---
account = {
    "usdc": 1000.0,
    "bnb": 50.0,
    "initial_value": 1050.0,
    "active_positions": {}, # Hier speichern wir die 3 Coins
    "pnl_history": []
}

@app.route('/')
def home():
    return f"Trading Bot Aktiv: {len(account['active_positions'])} Positionen offen. PnL: {account.get('last_pnl', 0):.2f}%"

def run_scanner():
    print("--- 🛰️ RADAR GESTARTET (3 COINS / 15-MIN PING) ---", flush=True)

    while True:
        now = datetime.now()
        
        try:
            # 1. SIMULATION VON 3 VERSCHIEDENEN SIGNALEN
            signals = [
                {"coin": "AXS", "apr_jump": 50},
                {"coin": "MOVE", "apr_jump": 35},
                {"coin": "SAFE", "apr_jump": 20}
            ]

            for sig in signals:
                coin = sig['coin']
                # Nur kaufen, wenn wir noch Platz für 3 Coins haben und noch nicht investiert sind
                if len(account['active_positions']) < 3 and coin not in account['active_positions']:
                    investment = 200 # Wir setzen 200 USDC pro Coin
                    account['usdc'] -= investment
                    account['bnb'] -= 0.15 # Gebühr
                    account['active_positions'][coin] = investment
                    print(f"🚀 KAUF: {coin} (APR +{sig['apr_jump']}%) | -200 USDC", flush=True)

            # 2. DER 15-MINUTEN PING (Status-Update)
            if now.minute % 15 == 0 and now.second < 30:
                # Berechne aktuellen Wert (Simulierter kleiner Profit von 2% für den Test)
                current_assets_value = sum(account['active_positions'].values()) * 1.02 
                total_now = account['usdc'] + account['bnb'] + current_assets_value
                pnl = ((total_now - account['initial_value']) / account['initial_value']) * 100
                account['last_pnl'] = pnl
                
                print(f"\n⏱️ 15-MINUTEN STATUS ({now.strftime('%H:%M')})", flush=True)
                print(f"💰 USDC: {account['usdc']:.2f} | BNB: {account['bnb']:.2f}", flush=True)
                print(f"📊 Aktive Coins: {list(account['active_positions'].keys())}", flush=True)
                print(f"📈 Aktuelle PnL: {pnl:.2f}%", flush=True)
                print("-" * 30, flush=True)
                
                time.sleep(31) # Verhindert Doppel-Logs in der gleichen Minute

        except Exception as e:
            print(f"⚠️ Fehler: {e}", flush=True)

        time.sleep(30)

threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
