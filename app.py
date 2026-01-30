import os
import ccxt
import time
from flask import Flask
import threading
from datetime import datetime

app = Flask(__name__)

# --- VIRTUELLES TEST-KONTO ---
account = {
    "usdc": 1000.0,
    "bnb": 50.0,
    "initial_value": 1050.0, # Startwert gesamt
    "trades": 0,
    "pnl": 0.0
}

apr_memory = {"binance": {}, "bybit": {}}

@app.route('/')
def home():
    return f"Trading Bot: Demo läuft. Stand: {account['usdc']:.2f} USDC | PnL: {account['pnl']:.2f}%"

def run_scanner():
    print("--- 🛰️ START DER SIMULATION (START: 1000 USDC / 50 BNB) ---", flush=True)

    while True:
        now = datetime.now()
        
        try:
            # 1. APR-RADAR (Simulierte Signale für den Testlauf)
            # Hier imitieren wir einen APR-Sprung bei einem Token (z.B. AXS)
            test_signal = {"coin": "AXS", "old_apr": 15.0, "new_apr": 65.0} # 333% Anstieg!
            
            # 2. STRATEGIE-EXECUTION (Demo)
            if test_signal['new_apr'] > test_signal['old_apr'] * 1.5:
                # Simulierter Kauf: 100 USDC investieren
                fee = 0.10 # 0.10 USD Gebühr in BNB
                account['usdc'] -= 100
                account['bnb'] -= fee
                account['trades'] += 1
                
                # Simulierter Profit (z.B. 5% Profit laut Freitags-Regel)
                profit = 5.0 
                account['usdc'] += 105.0 # Rückfluss inkl. Gewinn
                
                print(f"🚀 SIGNAL: {test_signal['coin']} APR Sprung! Trade ausgeführt.", flush=True)

            # 3. DAS 21:00 UHR REPORTING
            if now.hour == 21 and now.minute == 0:
                current_total = account['usdc'] + account['bnb']
                account['pnl'] = ((current_total - account['initial_value']) / account['initial_value']) * 100
                
                print("\n" + "="*40, flush=True)
                print(f"📊 TAGESBERICHT 21:00 UHR", flush=True)
                print(f"💰 USDC Stand: {account['usdc']:.2f}", flush=True)
                print(f"⛽ BNB Stand (Gebühren): {account['bnb']:.2f}", flush=True)
                print(f"🔄 Trades heute: {account['trades']}", flush=True)
                print(f"📈 PnL Gesamt: {account['pnl']:.2f}%", flush=True)
                print("="*40 + "\n", flush=True)
                
                # Um Mehrfach-Reports in der gleichen Minute zu verhindern
                time.sleep(61)

        except Exception as e:
            print(f"⚠️ Fehler: {e}", flush=True)

        time.sleep(30) # Check alle 30 Sekunden

threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
