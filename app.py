import os
import time
import requests
import threading
from flask import Flask
from datetime import datetime

app = Flask(__name__)

# --- DEINE TELEGRAM DATEN (BEREITS EINGEFÜGT) ---
TELEGRAM_TOKEN = "8597158635:AAFL3ah1yxQwXV9ntnChwY9sZRl6mcemt5s"
TELEGRAM_CHAT_ID = 5810124088

# --- VIRTUELLES KONTO FÜR DEN TRADING BOT ---
account = {
    "usdc": 1000.0,
    "bnb": 50.0,
    "initial_value": 1050.0,
    "active_positions": {},
    "last_pnl": 0.0
}

def send_telegram(message):
    """Hilfsfunktion für Telegram-Nachrichten"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram Fehler: {e}")

@app.route('/')
def home():
    # Anzeige für die Render-Webseite
    pos_list = ", ".join(account['active_positions'].keys()) if account['active_positions'] else "Keine"
    return f"Bot läuft! <br>Aktive Coins: {pos_list} <br>Aktuelle PnL: {account['last_pnl']:.2f}%"

def run_scanner():
    print("--- 🚀 BOT GESTARTET: 3-COIN-MODUS & TELEGRAM ---")
    # Erste Nachricht beim Start
    send_telegram("✅ *Trading Bot Online!*\nIch überwache jetzt AXS, MOVE & SAFE für dich.")

    while True:
        now = datetime.now()
        
        try:
            # 1. SCAN LOGIK: Simuliert Signale für 3 verschiedene Coins
            signals = [
                {"coin": "AXS", "apr": 55},
                {"coin": "MOVE", "apr": 42},
                {"coin": "SAFE", "apr": 28}
            ]

            for sig in signals:
                coin = sig['coin']
                # Kaufe bis zu 3 verschiedene Coins gleichzeitig
                if len(account['active_positions']) < 3 and coin not in account['active_positions']:
                    investment = 200.0
                    account['usdc'] -= investment
                    account['bnb'] -= 0.15 # Simulierte Netzwerkgebühr
                    account['active_positions'][coin] = investment
                    send_telegram(f"🚀 *Kauf-Signal:* {coin}\n📈 APR Sprung: {sig['apr']}%\n💰 Einsatz: 200.00 USDC")

            # 2. 15-MINUTEN STATUS-UPDATE PER TELEGRAM (z.B. 14:00, 14:15, 14:30...)
            if now.minute % 15 == 0 and now.second < 30:
                # Simulierter Wert (kleine Schwankung für den Test)
                current_value = sum(account['active_positions'].values()) * 1.015 
                total_now = account['usdc'] + account['bnb'] + current_value
                pnl = ((total_now - account['initial_value']) / account['initial_value']) * 100
                account['last_pnl'] = pnl
                
                status_msg = (
                    f"⏱️ *15-Minuten Status*\n"
                    f"💰 Kontostand: {total_now:.2f} (USDC/BNB)\n"
                    f"📈 Aktuelle PnL: *{pnl:.2f}%*\n"
                    f"📊 Aktive Coins: {', '.join(account['active_positions'].keys())}"
                )
                send_telegram(status_msg)
                time.sleep(31) # Verhindert, dass er in derselben Minute zweimal sendet

        except Exception as e:
            print(f"Fehler im Loop: {e}")

        time.sleep(30) # Scant alle 30 Sekunden

# Startet den Scanner in einem Hintergrund-Thread
threading.Thread(target=run_scanner, daemon=True).start()

if __name__ == "__main__":
    # Port-Einstellung für Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
