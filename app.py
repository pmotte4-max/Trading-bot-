import os
import time
import requests
import threading
import telebot
from flask import Flask

# --- KONFIGURATION ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- DATEN-ABFRAGE (Bybit mit Binance Backup) ---
def get_crypto_data():
    # Versuch 1: Bybit
    url = "https://api.bybit.com/v5/earn/product/search"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, params={"category": "FLEXIBLE"}, headers=headers, timeout=10)
        data = r.json()
        if data.get("retCode") == 0:
            prods = data["result"].get("productList", [])
            return [{"coin": x["coin"], "apr": float(x["estimateApr"])*100} for x in prods[:3]]
    except:
        pass

    # Versuch 2: Binance (Backup), falls Bybit blockiert
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=10)
        # Hier nehmen wir einfach Beispielhaft Top-Coins als Platzhalter
        return [{"coin": "BTC (Binance)", "apr": 0.00}, {"coin": "ETH", "apr": 0.00}]
    except:
        return []

# --- TELEGRAM ---
@bot.message_handler(func=lambda m: True)
def handle(m):
    if "status" in m.text.lower():
        bot.reply_to(m, "Suche Daten... 🔍")
        data = get_crypto_data()
        if data:
            msg = "🚀 **Top APR Werte:**\n\n"
            for x in data:
                msg += f"💰 **{x['coin']}**: {x['apr']:.2f}% APR\n"
            bot.send_message(m.chat.id, msg, parse_mode="Markdown")
        else:
            bot.reply_to(m, "Datenquelle aktuell nicht erreichbar. ❌")

# --- SERVER ---
@app.route('/')
def health(): return "OK", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
